import DashboardSidebar from "@/components/dashboard-sidebar";

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  return (
   <DashboardSidebar>
    {children}
   </DashboardSidebar>
  );
}
