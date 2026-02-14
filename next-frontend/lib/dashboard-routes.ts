import ChatSidebarPane from "@/components/sidebar-panes/chat-pane";
import EmailsSidebarPane from "@/components/sidebar-panes/emails-pane";
import {
  ArchiveX,
  BotMessageSquare,
  Calendar,
  CircleQuestionMark,
  LucideIcon,
  Settings,
  Star,
} from "lucide-react";
import { JSX } from "react";

type NavRouteItems = {
  title: string;
  url: string;
};

type NavRouteWithSubSidebar = {
  title: string;
  url: string;
  items?: NavRouteItems[];
  icon: LucideIcon;
  enableSubSidebar: true; // indicates if the route requires a sub sidebar
  pane: () => JSX.Element;
  type: "primary" | "secondary";
};

type NavRouteWithoutSubSidebar = {
  title: string;
  url: string;
  items?: NavRouteItems[];
  enableSubSidebar: false; // indicates if the route requires a sub sidebar
  icon: LucideIcon;
  type: "primary" | "secondary";
};

export type NavRoute = NavRouteWithSubSidebar | NavRouteWithoutSubSidebar;

export const DASHBOARD_ROUTES: NavRoute[] = [
  // MAIN NAv
  {
    title: "Inbox",
    url: "/inbox",
    icon: ArchiveX,
    pane: () => {
      return EmailsSidebarPane({ type: "Inbox" });
    },
    type: "primary",
    enableSubSidebar: true,
  },
  {
    title: "Starred",
    url: "/starred",
    icon: Star,
    pane: () => {
      return EmailsSidebarPane({ type: "Starred" });
    },
    type: "primary",
    enableSubSidebar: true,
  },
  {
    title: "Calendar",
    url: "/calendar",
    icon: Calendar,
    type: "primary",
    enableSubSidebar: false,
  },
  {
    title: "Chat with us",
    icon: BotMessageSquare,
    pane: ChatSidebarPane,
    url: "/chat",
    type: "primary",
    enableSubSidebar: true,
  },
  // SECONDARY NAV
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
    type: "secondary",
    enableSubSidebar: false,
  },
  {
    title: "Support",
    url: "/support",
    icon: CircleQuestionMark,
    type: "secondary",
    enableSubSidebar: false,
  },
];
