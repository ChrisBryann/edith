type DashboardRouteItems = {
  title: string;
  url: string;
};

export type DashboardRoute = {
  title: string;
  url: string;
  items?: DashboardRouteItems[];
};

export const DASHBOARD_ROUTES: DashboardRoute[] = [
  {
    title: "Your Emails",
    url: "/emails",
    items: [
      {
        title: "Inbox",
        url: "/emails?type=inbox",
      },
      {
        title: "Starred",
        url: "/emails?type=starred",
      },
    ],
  },
  {
    title: "Chat with us",
    url: "/chat",
  },
  {
    title: "Settings",
    url: "/settings",
  },
];
