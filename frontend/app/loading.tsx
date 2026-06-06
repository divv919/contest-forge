import { Skeleton } from "@/components/ui/skeleton"

export  function Loading() {
  return <Skeleton className="h-[60vh] w-full rounded-3xl" />
}

export default function AppLoading() {
  return <Loading />
}