import { TCalendarView } from "@/calendar/types";
import CalendarPage from "@/components/calendar";

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ view: TCalendarView }>;
}) {
  const params = await searchParams;
  const view = params.view ?? "month";
  console.log(view)
  return <CalendarPage view={view} />;
}
