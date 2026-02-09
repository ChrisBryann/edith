"use client";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
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
import { DASHBOARD_ROUTES, DashboardRoute } from "@/lib/dashboard-routes";
import { usePathname, useSearchParams } from "next/navigation";
import path from "path";

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

  const findRoute = (currentUrl: string) => {
    for (const parent of DASHBOARD_ROUTES) {
      // match parent directly
      if (parent.url === currentUrl) {
        return { parentRoute: parent, childRoute: null };
      }

      // match child
      for (const child of parent.items ?? []) {
        if (child.url === currentUrl) {
          return { parentRoute: parent, childRoute: child };
        }
      }
    }

    return { parentRoute: null, childRoute: null };
  };

  const { parentRoute, childRoute } = findRoute(currentUrl);

  useEffect(() => {
    console.log(currentUrl);
  }, [currentUrl]);

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "19rem",
        } as React.CSSProperties
      }
    >
      <AppSidebar currentRouteUrl={currentUrl} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 px-4">
          <SidebarTrigger className="-ms-1" />
          <Separator
            orientation="vertical"
            className="me-2 data-vertical:h-4 data-vertical:self-auto"
          />
          <Breadcrumb>
            <BreadcrumbList>
              {parentRoute && (
                <>
                  <BreadcrumbItem className="hidden md:block">
                    <BreadcrumbLink href={parentRoute.url}>
                      {parentRoute?.title ?? ""}
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  {childRoute && <BreadcrumbSeparator className="hidden md:block" />}
                </>
              )}

              <BreadcrumbItem>
                <BreadcrumbPage>{childRoute?.title ?? ""}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="ml-auto flex gap-4">
            <ModeToggle />
            <Button className="rounded-lg">Log in</Button>
          </div>
        </header>
        {children}
      </SidebarInset>
    </SidebarProvider>
  );
}
