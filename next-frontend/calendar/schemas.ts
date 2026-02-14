import { z } from "zod";

export const eventSchema = z
  .object({
    user: z.string().optional(), // TODO: Determine if user field is required
    title: z.string({error: "Title is required"}).min(1),
    description: z.string({error: "Description is required"}).min(1),
    startDate: z.date({ error: "Start date is required" }),
    startTime: z.object({ hour: z.number(), minute: z.number() }, { error: "Start time is required" }),
    endDate: z.date({ error: "End date is required" }),
    endTime: z.object({ hour: z.number(), minute: z.number() }, { error: "End time is required" }),
    color: z.enum(["blue", "green", "red", "yellow", "purple", "orange", "gray"], { error: "Color is required" }),
  })
  .refine(
    data => {
      const startDateTime = new Date(data.startDate);
      startDateTime.setHours(data.startTime.hour, data.startTime.minute, 0, 0);

      const endDateTime = new Date(data.endDate);
      endDateTime.setHours(data.endTime.hour, data.endTime.minute, 0, 0);

      return startDateTime < endDateTime;
    },
    {
      message: "Start date cannot be after end date",
      path: ["startDate"],
    }
  );

export type TEventFormData = z.infer<typeof eventSchema>;
