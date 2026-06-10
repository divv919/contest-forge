import Protected from "@/components/auth/Protected";
import ProblemWorkspace from "@/components/problems/ProblemWorkspace";

export default async function ProblemPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return (
    <Protected>
      <ProblemWorkspace slug={slug} />
    </Protected>
  );
}
