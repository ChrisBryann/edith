"use client";

import * as React from "react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInput,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import { DASHBOARD_ROUTES } from "@/lib/dashboard-routes";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export function AppSidebar({
  currentRouteUrl,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  currentRouteUrl: string;
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
    refetchInterval: 20000, // every 20 seconds
  });

  if (statusError) console.log(statusError);

  return (
    <Sidebar
      collapsible="icon"
      className="overflow-hidden *:data-[sidebar=sidebar]:flex-row"
      {...props}
    >
      <Sidebar
        collapsible="none"
        className="w-[calc(var(--sidebar-width-icon)+10px)]! border-r"
      >
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" asChild>
                <button>
                  <div className="flex flex-col gap-0.5 leading-none">
                    <span className="font-medium text-xl">edith.</span>
                    <span className="">v1.0.0</span>
                  </div>
                </button>
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
        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                className={`py-6 ${isStatusLoading ? "text-white" : isStatusError ? "text-red-500" : "text-green-500"}`}
              >
                {isStatusLoading
                  ? "Syncing..."
                  : isStatusError
                    ? "Offline"
                    : "Online & Synced"}
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
      <Sidebar collapsible="none" className="hidden flex-1 md:flex">
        <SidebarHeader className="gap-3.5 border-b p-4">
          <div className="flex w-full items-center justify-between">
            <div className="text-foreground text-base font-medium">Inbox</div>
            <Label className="flex items-center gap-2 text-sm">
              <span>Unreads</span>
              <Switch className="shadow-none" />
            </Label>
          </div>
          <SidebarInput placeholder="Type to search..." />
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup className="px-0">
            <SidebarGroupContent>
              {[
                {
                  name: "William Smith",
                  email: "williamsmith@example.com",
                  subject: "Meeting Tomorrow",
                  date: "09:34 AM",
                  teaser:
                    "Hi team, just a reminder about our meeting tomorrow at 10 AM.\nPlease come prepared with your project updates.",
                },
              ].map((mail) => (
                <a
                  href="#"
                  key={mail.email}
                  className="hover:bg-sidebar-accent hover:text-sidebar-accent-foreground flex flex-col items-start gap-2 border-b p-4 text-sm leading-tight whitespace-nowrap last:border-b-0"
                >
                  <div className="flex w-full items-center gap-2">
                    <span>{mail.name}</span>{" "}
                    <span className="ml-auto text-xs">{mail.date}</span>
                  </div>
                  <span className="font-medium">{mail.subject}</span>
                  <span className="line-clamp-2 w-[260px] text-xs whitespace-break-spaces">
                    {mail.teaser}
                  </span>
                </a>
              ))}
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
    </Sidebar>
  );
}