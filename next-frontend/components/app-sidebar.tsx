"use client";

import * as React from "react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import { GalleryVerticalEndIcon } from "lucide-react";
import { DASHBOARD_ROUTES, DashboardRoute } from "@/lib/dashboard-routes";
import Link from "next/link";

export function AppSidebar({
  currentRouteUrl,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  currentRouteUrl: string;
}) {
  return (
    <Sidebar variant="floating" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="#">
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-medium text-xl">edith.</span>
                  <span className="">v1.0.0</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu className="gap-2">
            {DASHBOARD_ROUTES.map((parent_item) => (
              <SidebarMenuItem key={parent_item.title}>
                <SidebarMenuButton
                  asChild
                  isActive={currentRouteUrl === parent_item.url}
                >
                  <Link href={parent_item.url} className="font-medium">
                    {parent_item.title}
                  </Link>
                </SidebarMenuButton>
                {parent_item.items?.length ? (
                  <SidebarMenuSub className="ms-0 border-s-0 px-1.5">
                    {parent_item.items.map((item) => (
                      <SidebarMenuSubItem key={item.title}>
                        <SidebarMenuSubButton
                          asChild
                          isActive={currentRouteUrl === item.url}
                        >
                          <Link href={item.url}>{item.title}</Link>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    ))}
                  </SidebarMenuSub>
                ) : null}
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
