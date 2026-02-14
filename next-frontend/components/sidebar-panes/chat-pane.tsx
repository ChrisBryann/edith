"use client";
import { Label } from "@/components/ui/label";
import {
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInput,
} from "@/components/ui/sidebar";
import { Switch } from "@/components/ui/switch";
import Link from "next/link";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Button } from "../ui/button";
import { Ellipsis, FolderPlus, SquarePen, Star, Trash } from "lucide-react";

export default function ChatSidebarPane() {
  // TODO: fetch the chat
  const chats = [
    {
      id: "123194iwelnfenlf",
      title: "Update on Project Phoenix",
      isStarred: true,
    },
    {
      id: "3r480feu7f0eusjse23221a",
      title: "Upcoming events on March 2026",
      isStarred: false,
    },
    {
      id: "pu31u10r83ywpifjwpfjpds",
      title: "Info about Pokémon Center delivery",
      isStarred: false,
    },
    {
      id: "awei3u2pu4u2peksw2211",
      title: "What's going on with the NFL draft for 2026 Combine",
      isStarred: false,
    },
  ];
  return (
    <>
      <SidebarHeader className="gap-3.5 p-4">
        <div className="flex w-full items-center justify-between">
          <div className="text-foreground text-base font-medium">Chats</div>
        </div>
        <SidebarInput placeholder="Type to search..." />
      </SidebarHeader>
      <SidebarContent>
        {/* Recents */}
        <SidebarGroup className="px-0">
          <SidebarGroupContent>
            <div className="text-muted-foreground px-3 py-2">
              Recents
            </div>
            {chats.map((chat) => (
              <div
                key={chat.id}
                className="flex flex-row items-center w-full hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-sm px-1"
              >
                <Link href={`/chat?id=${chat.id}`} className="pl-2 grow line-clamp-1">
                  {chat.title}
                </Link>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button className="shrink-0 z-10" variant="ghost">
                      <Ellipsis size="sm" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-40">
                    <DropdownMenuItem>
                      <Star size="sm" />
                      Star
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <SquarePen size="sm" />
                      Rename
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <FolderPlus size="sm" />
                      Add to project
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-red-500">
                      <Trash size="sm" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))}
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </>
  );
}
