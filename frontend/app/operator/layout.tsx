import { redirect } from "next/navigation";
import { getViewerContext } from "@/lib/viewer/session";

export default async function OperatorLayout({ children }: { children: React.ReactNode }) {
  const viewer = await getViewerContext();

  if (!viewer.canSeeOperatorDepth) {
    redirect("/app");
  }

  return children;
}
