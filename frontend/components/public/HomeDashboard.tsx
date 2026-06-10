"use client";
// Hi
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpenText,
  Clock3,
  Layers3,
  Trophy,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { MetricCard } from "@/components/shared/MetricCard";
import { PageHeader } from "@/components/shared/PageHeader";
import { ContestCard } from "@/components/contests/ContestCard";
import { ProblemCard } from "@/components/problems/ProblemCard";
import {
  getOngoingContests,
  getPastContests,
  getProblems,
  getUpcomingContests,
} from "@/lib/api/catalog";
import { getContestState } from "@/lib/catalog";
import type { Contest, Problem } from "@/lib/types";

type LoadState = {
  loading: boolean;
  error: string | null;
  problems: Problem[];
  contests: Contest[];
};

export function HomeDashboard() {
  const [state, setState] = useState<LoadState>({
    loading: true,
    error: null,
    problems: [],
    contests: [],
  });
  const [query, setQuery] = useState("");

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const [problems, upcoming, ongoing, past] = await Promise.all([
          getProblems(),
          getUpcomingContests(),
          getOngoingContests(),
          getPastContests(),
        ]);

        if (!active) return;

        setState({
          loading: false,
          error: null,
          problems,
          contests: [...ongoing, ...upcoming, ...past],
        });
      } catch (error) {
        if (!active) return;

        setState({
          loading: false,
          error:
            error instanceof Error
              ? error.message
              : "Unable to load catalog data",
          problems: [],
          contests: [],
        });
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);

  const stats = useMemo(() => {
    const upcoming = state.contests.filter(
      (contest) => getContestState(contest) === "upcoming",
    ).length;
    const ongoing = state.contests.filter(
      (contest) => getContestState(contest) === "ongoing",
    ).length;
    const past = state.contests.filter(
      (contest) => getContestState(contest) === "past",
    ).length;

    return [
      {
        label: "Problems",
        value: String(state.problems.length),
        note: "Ready for the next solve session",
      },
      {
        label: "Live contests",
        value: String(ongoing),
        note: "Currently accepting submissions",
      },
      {
        label: "Upcoming",
        value: String(upcoming),
        note: "Scheduled contests at a glance",
      },
      {
        label: "Finished",
        value: String(past),
        note: "Archived for rankings and history",
      },
    ];
  }, [state.contests, state.problems.length]);

  const featuredProblems = state.problems
    .filter(
      (problem) =>
        problem.name.toLowerCase().includes(query.toLowerCase()) ||
        problem.slug.toLowerCase().includes(query.toLowerCase()),
    )
    .slice(0, 3);
  const featuredContests = state.contests
    .filter(
      (contest) =>
        contest.name.toLowerCase().includes(query.toLowerCase()) ||
        contest.slug.toLowerCase().includes(query.toLowerCase()),
    )
    .slice(0, 3);

  return (
    <div className="space-y-8 pb-12">
      <PageHeader
        eyebrow="Contest platform"
        title="Brow, track contests, and jump straight into the solve loop."
        description="The public surface stays useful before sign-in, and the same catalog powers the rest of the product shell once a token is present."
        actions={
          <>
            <Button asChild>
              <Link href="/problems">
                Explore problems
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/contests">View contests</Link>
            </Button>
          </>
        }
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <MetricCard key={stat.label} {...stat} />
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.6fr_1fr]">
        <Card className="overflow-hidden bg-[linear-gradient(135deg,rgba(15,23,42,0.96),rgba(15,23,42,0.82),rgba(28,25,23,0.9))] text-white">
          <CardContent className="grid gap-6 p-6 sm:p-8">
            <div className="flex flex-wrap gap-3 text-sm text-white/80">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1">
                <Clock3 className="size-3.5" />
                Contest timing
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1">
                <Layers3 className="size-3.5" />
                Problem catalog
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1">
                <Trophy className="size-3.5" />
                Ranked after finalization
              </span>
            </div>
            <div className="space-y-3">
              <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
                Use the same catalog view for public browsing and authenticated
                solving.
              </h2>
              <p className="max-w-2xl text-sm leading-6 text-white/75 sm:text-base">
                Search once, then jump from a problem card into the dedicated
                statement route or from a contest card into the contest shell
                without leaving the current product language behind.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button asChild variant="secondary">
                <Link href="/login">Sign in to submit</Link>
              </Button>
              <Button
                asChild
                variant="outline"
                className="border-white/15 bg-white/5 text-white hover:bg-white/10 hover:text-white"
              >
                <Link href="/register">Create account</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 p-6">
            <div className="space-y-1">
              <h3 className="text-sm font-semibold uppercase tracking-[0.22em] text-muted-foreground">
                Quick search
              </h3>
              <p className="text-sm text-muted-foreground">
                Filter the previwww cards before opening the catalog pages.
              </p>
            </div>
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search problems or contests"
            />
            <Separator />
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-medium">
                <BookOpenText className="size-4 text-muted-foreground" />
                Public preview
              </div>
              <p className="text-sm leading-6 text-muted-foreground">
                The pages below show a live slice of the catalog. If the backend
                is unreachable or the current session is not authorized, the
                page still renders the empty and error states rather than
                failing silently.
              </p>
            </div>
          </CardContent>
        </Card>
      </section>

      {state.loading ? (
        <HomeSkeleton />
      ) : state.error ? (
        <EmptyState
          title="Unable to load the catalog"
          description={state.error}
          actionHref="/login"
          actionLabel="Sign in and retry"
        />
      ) : (
        <>
          <section className="space-y-4">
            <div className="flex items-end justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold tracking-tight">
                  Featured problems
                </h2>
                <p className="text-sm text-muted-foreground">
                  A compact sample from the public problem list.
                </p>
              </div>
              <Button asChild variant="ghost">
                <Link href="/problems">See all problems</Link>
              </Button>
            </div>
            {featuredProblems.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {featuredProblems.map((problem) => (
                  <ProblemCard key={problem.slug} problem={problem} />
                ))}
              </div>
            ) : (
              <EmptyState
                title="No matching problems"
                description="Try a broader search or clear the query to show the default catalog sample."
                actionHref="/problems"
                actionLabel="Open the full catalog"
              />
            )}
          </section>

          <section className="space-y-4">
            <div className="flex items-end justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold tracking-tight">
                  Featured contests
                </h2>
                <p className="text-sm text-muted-foreground">
                  Upcoming, ongoing, and finished contests from the same source
                  data.
                </p>
              </div>
              <Button asChild variant="ghost">
                <Link href="/contests">See all contests</Link>
              </Button>
            </div>
            {featuredContests.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {featuredContests.map((contest) => (
                  <ContestCard key={contest.slug} contest={contest} />
                ))}
              </div>
            ) : (
              <EmptyState
                title="No matching contests"
                description="Try a broader search or clear the query to show the default contest sample."
                actionHref="/contests"
                actionLabel="Open the contest list"
              />
            )}
          </section>
        </>
      )}
    </div>
  );
}

function HomeSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-56 w-full rounded-3xl" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Skeleton key={index} className="h-28 rounded-2xl" />
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="h-48 rounded-2xl" />
        ))}
      </div>
    </div>
  );
}
