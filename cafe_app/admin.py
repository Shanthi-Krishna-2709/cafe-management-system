import json
from collections import defaultdict

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib import messages
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils import timezone

from .menu_catalog import MENU_CATALOG
from .models import Category, Menu, Order, OrderError


class CafeAdminSite(AdminSite):
    site_header = "Cafe control room"
    site_title = "Cafe admin"
    index_title = "Admin Dashboard"
    index_template = "admin/cafe_dashboard.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "sync-menu/",
                self.admin_view(self.sync_menu_view),
                name="sync_menu",
            ),
            path(
                "sales-report/",
                self.admin_view(self.sales_report_view),
                name="sales_report",
            ),
        ]
        return custom_urls + urls

    def _menu_overview(self):
        grouped_items = defaultdict(list)
        for item in Menu.objects.select_related("category").order_by("category__name", "name"):
            category_name = item.category.name if item.category else "Uncategorized"
            grouped_items[category_name].append(item)
        return grouped_items

    def _top_items(self):
        sold_items = defaultdict(lambda: {"qty": 0, "revenue": 0.0})

        for order in Order.objects.all():
            try:
                order_items = json.loads(order.items or "[]")
            except json.JSONDecodeError:
                continue

            for item in order_items:
                name = item.get("name", "Unknown item")
                qty = int(item.get("qty", 0) or 0)
                revenue = float(item.get("price", 0) or 0)
                sold_items[name]["qty"] += qty
                sold_items[name]["revenue"] += revenue

        top_items = sorted(
            [
                {
                    "name": name,
                    "qty": values["qty"],
                    "revenue": values["revenue"],
                }
                for name, values in sold_items.items()
            ],
            key=lambda entry: (-entry["qty"], -entry["revenue"], entry["name"]),
        )
        return top_items[:6]

    def _decoded_items(self, order):
        try:
            return json.loads(order.items or "[]")
        except json.JSONDecodeError:
            return []

    def _dashboard_context(self):
        today = timezone.localdate()
        week_start = today - timezone.timedelta(days=6)

        orders = Order.objects.all()
        today_orders = orders.filter(created_at__date=today)
        weekly_orders = orders.filter(created_at__date__gte=week_start)
        completed_orders = orders.filter(status="completed")

        total_revenue = orders.aggregate(total=Sum("total_amount"))["total"] or 0
        today_revenue = today_orders.aggregate(total=Sum("total_amount"))["total"] or 0
        weekly_revenue = weekly_orders.aggregate(total=Sum("total_amount"))["total"] or 0
        completed_revenue = completed_orders.aggregate(total=Sum("total_amount"))["total"] or 0
        total_orders = orders.count()
        avg_order_value = total_revenue / total_orders if total_orders else 0

        payment_breakdown = list(
            orders.values("payment_method")
            .annotate(count=Count("id"), total=Sum("total_amount"))
            .order_by("-total")
        )
        status_breakdown = list(
            orders.values("status")
            .annotate(count=Count("id"), total=Sum("total_amount"))
            .order_by("-count")
        )
        payment_total = sum((row["total"] or 0) for row in payment_breakdown) or 1

        menu_lookup = {item.name: item.category.name for item in Menu.objects.select_related("category")}
        category_sales = defaultdict(lambda: {"qty": 0, "revenue": 0.0})
        total_items_sold = 0
        recent_orders = []

        for order in orders[:8]:
            decoded_items = self._decoded_items(order)
            recent_orders.append(
                {
                    "instance": order,
                    "items_summary": ", ".join(item.get("name", "Item") for item in decoded_items[:3]) or "No items",
                }
            )

        for order in completed_orders:
            for item in self._decoded_items(order):
                name = item.get("name", "Unknown item")
                qty = int(item.get("qty", 0) or 0)
                revenue = float(item.get("price", 0) or 0)
                category_name = menu_lookup.get(name, "Other")
                category_sales[category_name]["qty"] += qty
                category_sales[category_name]["revenue"] += revenue
                total_items_sold += qty

        category_breakdown = sorted(
            [
                {"name": name, "qty": values["qty"], "revenue": values["revenue"]}
                for name, values in category_sales.items()
            ],
            key=lambda entry: (-entry["revenue"], entry["name"]),
        )
        category_total = sum(entry["revenue"] for entry in category_breakdown) or 1

        daily_breakdown = []
        daily_max = 0
        for day_offset in range(6, -1, -1):
            day = today - timezone.timedelta(days=day_offset)
            day_orders = orders.filter(created_at__date=day)
            revenue = day_orders.aggregate(total=Sum("total_amount"))["total"] or 0
            order_count = day_orders.count()
            daily_max = max(daily_max, revenue)
            daily_breakdown.append(
                {
                    "label": day.strftime("%a"),
                    "date": day.strftime("%d %b"),
                    "orders": order_count,
                    "revenue": revenue,
                }
            )

        daily_max = daily_max or 1
        for row in daily_breakdown:
            row["height_pct"] = max(10, round((row["revenue"] / daily_max) * 100)) if row["revenue"] else 8

        for row in payment_breakdown:
            row["pct"] = round(((row["total"] or 0) / payment_total) * 100, 1)

        for row in category_breakdown:
            row["pct"] = round((row["revenue"] / category_total) * 100, 1)

        return {
            "dashboard_cards": [
                {
                    "label": "Total sales",
                    "value": f"Rs. {total_revenue:.2f}",
                    "meta": f"{total_orders} total orders",
                },
                {
                    "label": "Today",
                    "value": f"Rs. {today_revenue:.2f}",
                    "meta": f"{today_orders.count()} orders on {today.strftime('%d %b %Y')}",
                },
                {
                    "label": "Last 7 days",
                    "value": f"Rs. {weekly_revenue:.2f}",
                    "meta": "Weekly cafe revenue",
                },
                {
                    "label": "Completed sales",
                    "value": f"Rs. {completed_revenue:.2f}",
                    "meta": f"{completed_orders.count()} completed orders",
                },
            ],
            "recent_orders": recent_orders,
            "top_items": self._top_items(),
            "menu_sections": self._menu_overview().items(),
            "menu_item_count": Menu.objects.count(),
            "category_count": Category.objects.count(),
            "payment_breakdown": payment_breakdown,
            "status_breakdown": status_breakdown,
            "category_breakdown": category_breakdown[:5],
            "daily_breakdown": daily_breakdown,
            "avg_order_value": avg_order_value,
            "total_items_sold": total_items_sold,
            "total_orders_count": total_orders,
            "pending_orders_count": orders.filter(status="pending").count(),
            "sales_report_url": reverse("admin:sales_report"),
            "sync_menu_url": reverse("admin:sync_menu"),
            "orders_url": reverse("admin:cafe_app_order_changelist"),
            "menu_url": reverse("admin:cafe_app_menu_changelist"),
        }

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self._dashboard_context())
        return super().index(request, extra_context=extra_context)

    def sales_report_view(self, request):
        context = {
            **self.each_context(request),
            **self._dashboard_context(),
            "title": "Sales report",
        }
        return TemplateResponse(request, "admin/cafe_sales_report.html", context)

    def sync_menu_view(self, request):
        created_categories = 0
        created_items = 0
        updated_items = 0

        for section in MENU_CATALOG:
            category, category_created = Category.objects.get_or_create(name=section["category"])
            if category_created:
                created_categories += 1

            for item_data in section["items"]:
                menu_item, item_created = Menu.objects.update_or_create(
                    name=item_data["name"],
                    defaults={
                        "price": item_data["price"],
                        "category": category,
                    },
                )
                if item_created:
                    created_items += 1
                else:
                    updated_items += 1

        self.message_user(
            request,
            f"Menu sync complete. Categories created: {created_categories}, items created: {created_items}, items updated: {updated_items}.",
            level=messages.SUCCESS,
        )
        return redirect("admin:index")


cafe_admin_site = CafeAdminSite(name="admin")


@admin.register(Category, site=cafe_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Menu, site=cafe_admin_site)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
    list_filter = ("category",)
    search_fields = ("name", "category__name")
    ordering = ("category__name", "name")


@admin.register(Order, site=cafe_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "total_amount", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("customer_name", "customer_email", "customer_phone")
    readonly_fields = ("created_at", "updated_at", "id")
    ordering = ("-created_at",)


@admin.register(OrderError, site=cafe_admin_site)
class OrderErrorAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("customer_name", "customer_email", "customer_phone", "error_message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    fields = (
        "customer_name",
        "customer_phone",
        "customer_email",
        "payment_method",
        "status",
        "items",
        "subtotal",
        "gst",
        "total_amount",
        "error_message",
        "created_at",
    )
