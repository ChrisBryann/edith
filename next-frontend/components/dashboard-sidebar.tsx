"use client";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/ui/dark-mode-toggle";
import { useEffect, useMemo, useState } from "react";
import { DASHBOARD_ROUTES, NavRoute } from "@/lib/dashboard-routes";
import { usePathname, useSearchParams } from "next/navigation";

export default function DashboardSidebar({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const currentUrl = useMemo(() => {
    return `${pathname}${searchParams.size > 0 ? `?${searchParams.toString()}` : ""}`;
  }, [pathname, searchParams]);

  //   const findRoute = (currentUrl: string) => {
  //     for (const parent of DASHBOARD_ROUTES) {
  //       // match parent directly
  //       if (currentUrl.includes(parent.url)) {
  //         return { parentRoute: parent };
  //       }
  //     }

  //     return { parentRoute: null };
  //   };

  //   const { parentRoute } = findRoute(currentUrl);

  const [activeItem, setActiveItem] = useState<NavRoute>(
    DASHBOARD_ROUTES.find((r) => currentUrl.includes(r.url)) ??
      DASHBOARD_ROUTES[0],
  );

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "400px",
        } as React.CSSProperties
      }
      defaultOpen={activeItem.enableSubSidebar} // keeps the sub sidebar visibility controlled when page loads
    >
      <AppSidebar activeItem={activeItem} setActiveItem={setActiveItem} />
      <SidebarInset className="flex flex-col overflow-hidden">
        <header className="flex h-16 shrink-0 items-center gap-2 px-4">
          <SidebarTrigger className="-ms-1" />
          <Separator
            orientation="vertical"
            className="me-2 data-vertical:h-4 data-vertical:self-auto"
          />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbPage>{activeItem.title ?? ""}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <div className="flex-1 overflow-hidden min-h-0">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
