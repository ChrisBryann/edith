"use client";

import * as React from "react";
import {
  CircleAlert,
  CircleCheck,
  Command,
  LoaderCircle,
} from "lucide-react";

import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { DASHBOARD_ROUTES, NavRoute } from "@/lib/dashboard-routes";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ModeToggle } from "./ui/dark-mode-toggle";

export function AppSidebar({
  activeItem,
  setActiveItem,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  activeItem: NavRoute;
  setActiveItem: React.Dispatch<React.SetStateAction<NavRoute>>;
}) {
  const {
    data: status,
    error: statusError,
    isLoading: isStatusLoading,
    isError: isStatusError,
  } = useQuery({
    queryKey: ["system-status"],
    queryFn: async () => {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/system-status`,
      );
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data);
      }

      return data;
    },
    staleTime: 30000, // 30 seconds
    refetchOnReconnect: true,
  });

  if (statusError) console.log(statusError);

  // Note: I'm using state to show active item.
  // IRL you should use the url/router.

  const { setOpen, isMobile } = useSidebar();

  React.useEffect(() => {
    if (!activeItem.enableSubSidebar) {
      setOpen(false);
    }
  }, [activeItem.enableSubSidebar, setOpen]);

  return (
    <Sidebar
      collapsible="icon"
      className={`${activeItem.type === "primary" ? "overflow-hidden *:data-[sidebar=sidebar]:flex-col  md:*:data-[sidebar=sidebar]:flex-row" : `${isMobile ? "w-full" : "w-[calc(var(--sidebar-width-icon)+1px)]!"} border-r`}`}
      {...props}
    >
      {/* This is the first sidebar */}
      {/* We disable collapsible and adjust width to icon. */}
      {/* This will make the sidebar appear as icons. */}
      <Sidebar
        collapsible="none"
        className={`${isMobile ? "w-full" : "w-[calc(var(--sidebar-width-icon)+1px)]!"} border-r`}
      >
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" asChild className="md:h-8 md:p-0">
                <a href="#">
                  <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                    <Command className="size-4" />
                  </div>
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate text-lg font-medium">edith.</span>
                    <span className="truncate text-xs">v1.0.0</span>
                  </div>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>
        {/* MAIN NAV */}
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent className="px-1.5 md:px-0">
              <SidebarMenu>
                {DASHBOARD_ROUTES.filter((r) => r.type === "primary").map(
                  (item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        tooltip={{
                          children: item.title,
                          hidden: isMobile,
                        }}
                        isActive={activeItem?.title === item.title}
                        className="px-2.5 md:px-2"
                      >
                        <Link
                          onClick={() => {
                            setActiveItem(item);
                          }}
                          href={item.url}
                          className="flex items-center gap-2 font-medium"
                        >
                          <item.icon />
                          <span className="md:hidden">{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ),
                )}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        {/* SECONDARY NAV */}
        <SidebarContent>
          <SidebarGroup className="mt-auto">
            <SidebarGroupContent className="px-1.5 md:px-0">
              <SidebarMenu>
                {DASHBOARD_ROUTES.filter((r) => r.type === "secondary").map(
                  (item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        tooltip={{
                          children: item.title,
                          hidden: isMobile,
                        }}
                        isActive={activeItem?.title === item.title}
                        className="px-2.5 md:px-2"
                      >
                        <Link
                          onClick={() => {
                            setActiveItem(item);
                          }}
                          href={item.url}
                          className="flex items-center gap-2 font-medium"
                        >
                          <item.icon />
                          <span className="md:hidden">{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ),
                )}
                <SidebarMenuItem key="toggle-mode">
                  <SidebarMenuButton
                    tooltip={{
                      children: "Toggle Mode",
                      hidden: isMobile,
                    }}
                    className="px-2.5 md:px-2"
                    asChild
                  >
                      <ModeToggle variant={"ghost"} />
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem key="system-status">
                  <SidebarMenuButton
                    tooltip={{
                      children: isStatusLoading
                        ? "Syncing..."
                        : isStatusError
                          ? "Offline"
                          : "Online & Synced",
                      hidden: isMobile,
                    }}
                    className="px-2.5 md:px-2"
                  >
                    <div className="flex items-center gap-2 font-medium">
                      {isStatusLoading ? (
                        <LoaderCircle className="animate-spin" />
                      ) : isStatusError ? (
                        <CircleAlert className="text-red-500" />
                      ) : (
                        <CircleCheck className="text-green-500" />
                      )}
                      <span
                        className={`md:hidden ${isStatusError ? "text-red-500" : "text-green-500"}`}
                      >
                        {isStatusLoading
                          ? "Syncing..."
                          : isStatusError
                            ? "Offline"
                            : "Online & Synced"}
                      </span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter>
          <NavUser
            user={{
              email: "ledjaldaed",
              name: "John Doe",
              avatar: "@/public/window.svg",
            }}
          />
        </SidebarFooter>
      </Sidebar>

      {/* This is the second sidebar */}
      {/* We disable collapsible and let it fill remaining space */}
      {/* Secondary sidebar is for MAIN NAV */}
      {activeItem.enableSubSidebar && (
        <Sidebar collapsible="none" className="flex">
          <activeItem.pane />
        </Sidebar>
      )}
    </Sidebar>
  );
}
