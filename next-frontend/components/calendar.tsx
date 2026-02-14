"use client";

import { ChangeBadgeVariantInput } from "@/calendar/components/change-badge-variant-input";
import { ClientContainer } from "@/calendar/components/client-container";
import { CalendarProvider } from "@/calendar/contexts/calendar-context";
import { TCalendarView } from "@/calendar/types";

type Props = {
  view: TCalendarView;
};

export default function CalendarPage({ view }: Props) {
  return (
    <CalendarProvider
      events={[]}
      users={[
        {
          id: "23131213",
          name: "Christopher Bryan",
          picturePath: null,
        },
      ]}
    >
      <div className="flex flex-col gap-4 p-4 pt-0">
        <ClientContainer view={view} />
        <ChangeBadgeVariantInput />
        {/* <div className="grid auto-rows-min gap-4 md:grid-cols-3">
      
      <div className="bg-muted/50 aspect-video rounded-xl" />
      <div className="bg-muted/50 aspect-video rounded-xl" />
      <div className="bg-muted/50 aspect-video rounded-xl" />
      </div>
      <div className="bg-muted/50 min-h-screen flex-1 rounded-xl md:min-h-min" /> */}
      </div>
    </CalendarProvider>
  );
}
