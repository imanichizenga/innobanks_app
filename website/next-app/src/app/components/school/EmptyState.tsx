export default function EmptyState({ message }: { message: string }) {
  return <div className="rounded-xl border border-dashed border-blue-200 bg-blue-50 p-6 text-center text-sm text-gray">{message}</div>;
}
