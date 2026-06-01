import Protected from "@/components/auth/Protected"
import SubmissionDetail from "@/components/submissions/SubmissionDetail"

export default function SubmissionPage({ params }: { params: { id: string } }) {
  const submissionId = Number(params.id)

  if (!Number.isFinite(submissionId)) {
    return <Protected>{null}</Protected>
  }

  return (
    <Protected>
      <SubmissionDetail submissionId={submissionId} />
    </Protected>
  )
}