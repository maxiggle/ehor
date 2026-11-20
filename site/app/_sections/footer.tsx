import { ArrowUpRight } from "@/app/_components/icons";
import { Logo } from "@/app/_components/logo";
import { Container } from "@/app/_components/ui";
import { links } from "@/app/_lib/links";

const columns = [
  {
    title: "Build",
    items: [
      ["Guide", links.guide],
      ["Quick start", links.quickStart],
      ["Wire protocol", links.protocol],
      ["Known limits", links.knownLimits],
    ],
  },
  {
    title: "Project",
    items: [
      ["GitHub", links.repo],
      ["PyPI", links.pypi],
      ["Releases", links.releases],
      ["Issues", links.issues],
    ],
  },
  {
    title: "Built on ehor",
    items: [
      ["ehor-near", links.escrowReadme],
      ["Escrow spec", links.escrowSpec],
      ["Contract on testnet", links.contract],
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-line">
      <Container className="grid gap-12 py-16 md:grid-cols-[1.2fr_2fr]">
        <div>
          <Logo id="footer-logo" className="h-8 w-auto text-ink" />
          <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted">
            Signed, encrypted, serverless messaging between AI agents, and a base for products built
            on it.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
          {columns.map((column) => (
            <div key={column.title}>
              <h2 className="text-sm font-semibold">{column.title}</h2>
              <ul className="mt-4 space-y-2.5">
                {column.items.map(([label, href]) => (
                  <li key={label}>
                    <a
                      href={href}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-sm text-muted transition-colors hover:text-ink"
                    >
                      {label}
                      <ArrowUpRight className="size-3" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Container>
      <Container className="flex flex-col gap-2 border-t border-line py-6 text-xs text-muted sm:flex-row sm:justify-between">
        <p>MIT licensed. Built in the open.</p>
        <p>
          Syncs over{" "}
          <a href={links.iroh} target="_blank" rel="noreferrer" className="hover:text-ink">
            iroh
          </a>
          . No server to run.
        </p>
      </Container>
    </footer>
  );
}
