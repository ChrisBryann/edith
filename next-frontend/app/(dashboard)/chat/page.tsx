import ChatPage from "@/components/chat";

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ id: string }>;
}) {
  const params = await searchParams;

  return <ChatPage id={params.id} />;
}
