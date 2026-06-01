import Protected from "@/components/auth/Protected"
import ProblemWorkspace from "@/components/problems/ProblemWorkspace"

export default function ProblemPage({ params }: { params: { slug: string } }) {
  return (
    <Protected>
      <ProblemWorkspace slug={params.slug} />
    </Protected>
  )
}