"use client";

import { useParams } from "next/navigation";
import { docPages, getDocBySlug, docSidebar, getAllDocSlugs } from "@/lib/docs-content";
import type { DocContentBlock } from "@/lib/docs-content";
import { CodeBlock } from "@/components/CodeBlock";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Info, Lightbulb, AlertTriangle } from "lucide-react";

function DocContentRenderer({ blocks }: { blocks: DocContentBlock[] }) {
  return (
    <div className="space-y-6">
      {blocks.map((block, idx) => {
        switch (block.type) {
          case "heading":
            return (
              <h2 key={idx} className="text-xl font-semibold tracking-tight mt-10 mb-4 text-white/90 border-b border-white/[0.06] pb-3">
                {block.value}
              </h2>
            );

          case "text":
            return (
              <p key={idx} className="text-[15px] text-white/60 leading-[1.8]">
                {block.value}
              </p>
            );

          case "code":
            return (
              <div key={idx} className="my-4">
                <CodeBlock code={block.value} language={block.language || "bash"} />
              </div>
            );

          case "list":
            return (
              <ul key={idx} className="space-y-2 my-4">
                {block.items?.map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-[15px] text-white/60">
                    <span className="text-tertiary mt-1 text-xs">●</span>
                    <span className="leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            );

          case "callout": {
            const config = {
              note: { icon: Info, border: "border-blue-500/30", bg: "bg-blue-500/5", iconColor: "text-blue-400", label: "Note" },
              tip: { icon: Lightbulb, border: "border-tertiary/30", bg: "bg-tertiary/5", iconColor: "text-tertiary", label: "Tip" },
              warning: { icon: AlertTriangle, border: "border-orange-500/30", bg: "bg-orange-500/5", iconColor: "text-orange-400", label: "Warning" },
            }[block.calloutType || "note"]!;
            const Icon = config.icon;
            return (
              <div key={idx} className={`p-4 rounded-lg border-l-4 ${config.border} ${config.bg} my-6`}>
                <div className="flex items-center gap-2 mb-2">
                  <Icon className={`size-4 ${config.iconColor}`} />
                  <span className={`text-xs font-semibold uppercase tracking-wider ${config.iconColor}`}>{config.label}</span>
                </div>
                <p className="text-sm text-white/60 leading-relaxed">{block.value}</p>
              </div>
            );
          }

          case "table":
            return (
              <div key={idx} className="my-6 overflow-x-auto rounded-lg border border-white/[0.08]">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/[0.08] bg-white/[0.02]">
                      {block.headers?.map((header, hi) => (
                        <th key={hi} className="px-4 py-3 text-left text-xs font-semibold text-white/50 uppercase tracking-wider">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {block.rows?.map((row, ri) => (
                      <tr key={ri} className="border-b border-white/[0.04] last:border-0 hover:bg-white/[0.02] transition-colors">
                        {row.map((cell, ci) => (
                          <td key={ci} className="px-4 py-3 text-white/60 font-mono text-[13px]">
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );

          default:
            return null;
        }
      })}
    </div>
  );
}

function getAdjacentPages(slug: string) {
  const allSlugs = getAllDocSlugs();
  const idx = allSlugs.indexOf(slug);
  const prev = idx > 0 ? getDocBySlug(allSlugs[idx - 1]) : null;
  const next = idx < allSlugs.length - 1 ? getDocBySlug(allSlugs[idx + 1]) : null;
  return { prev, next };
}

export default function DocPage() {
  const params = useParams();
  const slug = (params?.slug as string) || "introduction";
  const doc = getDocBySlug(slug);
  const content = docPages[slug];
  const { prev, next } = getAdjacentPages(slug);

  if (!doc || !content) {
    return (
      <div className="max-w-3xl mx-auto px-8 py-20 text-center">
        <h1 className="text-2xl font-bold mb-4">Page Not Found</h1>
        <p className="text-white/50 mb-8">This documentation page does not exist yet.</p>
        <Link href="/docs/introduction" className="text-tertiary hover:underline">
          ← Back to Introduction
        </Link>
      </div>
    );
  }

  return (
    <div className="w-full max-w-5xl px-8 md:px-12 lg:px-16 py-12 pb-24">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-white/30 mb-8 font-mono">
        <Link href="/docs/introduction" className="hover:text-white/50 transition-colors">docs</Link>
        <span>/</span>
        <span className="text-white/50">{slug}</span>
      </div>

      {/* Page Header */}
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight mb-3">{doc.title}</h1>
        <p className="text-lg text-white/50 leading-relaxed">{doc.description}</p>
      </header>

      {/* Content */}
      <DocContentRenderer blocks={content} />

      {/* Navigation Footer */}
      <div className="mt-20 pt-8 border-t border-white/[0.06] flex items-center justify-between">
        {prev ? (
          <Link
            href={`/docs/${prev.slug}`}
            className="flex items-center gap-2 text-sm text-white/40 hover:text-white transition-colors group"
          >
            <ChevronLeft className="size-4 group-hover:-translate-x-0.5 transition-transform" />
            <div>
              <div className="text-[10px] uppercase tracking-wider text-white/25 mb-0.5">Previous</div>
              <div>{prev.title}</div>
            </div>
          </Link>
        ) : <div />}
        {next ? (
          <Link
            href={`/docs/${next.slug}`}
            className="flex items-center gap-2 text-sm text-white/40 hover:text-white transition-colors group text-right"
          >
            <div>
              <div className="text-[10px] uppercase tracking-wider text-white/25 mb-0.5">Next</div>
              <div>{next.title}</div>
            </div>
            <ChevronRight className="size-4 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        ) : <div />}
      </div>
    </div>
  );
}
