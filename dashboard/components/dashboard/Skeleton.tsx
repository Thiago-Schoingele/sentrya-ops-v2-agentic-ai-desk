export function SkeletonDashboard() {
  return (
    <div className="grid gap-4">
      <div className="h-36 animate-pulse rounded-lg bg-white/[0.04]" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, index) => (
          <div key={index} className="h-28 animate-pulse rounded-lg bg-white/[0.04]" />
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-64 animate-pulse rounded-lg bg-white/[0.04]" />
        ))}
      </div>
    </div>
  );
}
