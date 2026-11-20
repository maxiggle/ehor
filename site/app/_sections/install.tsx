import { CodeLines, InstallTabs, type Snippet } from "@/app/_components/code-block";
import { GitHubIcon } from "@/app/_components/icons";
import { Mark } from "@/app/_components/logo";
import { Container, Em, Section } from "@/app/_components/ui";
import { links } from "@/app/_lib/links";

const start = `# install ehor from PyPI
uv tool install 'ehor[p2p]'

# start a team, or join one with ehor join eh1-...
ehor init --handle ada --team-name Acme

# start the sync service and keep it running
ehor serve`;

function shell(code: string): Snippet {
  return { language: "shell", code };
}

const tabs = [
  {
    label: "Claude Code",
    note: "--scope user makes ehor available in all your projects. ehor setup claude adds /inbox, /handoff and the other slash commands.",
    snippet: shell(`${start}

# connect Claude Code and add the slash commands
claude mcp add --scope user ehor -- ehor mcp
ehor setup claude`),
  },
  {
    label: "Codex",
    note: "Run /mcp in Codex to check that ehor is connected. ehor setup codex adds skills such as $ehor-inbox.",
    snippet: shell(`${start}

# connect Codex and add the skills
codex mcp add ehor -- ehor mcp
ehor setup codex`),
  },
  {
    label: "opencode",
    note: "In opencode mcp add, add a local server named ehor that runs ehor mcp. ehor setup opencode adds the slash commands.",
    snippet: shell(`${start}

# connect opencode: a local server named "ehor" running "ehor mcp"
opencode mcp add
ehor setup opencode`),
  },
];

const teammate = shell(`# your teammate, from any network
ehor join eh1-... --handle tobi

# you, as admin: add them to the roster
ehor roster add tobi 0372c4010a... --channel '#mobile'`);

export function Install() {
  return (
    <Section
      id="install"
      eyebrow="Get started"
      title={
        <>
          Pick your agent. <Em>Hand off work.</Em>
        </>
      }
      intro="Install ehor, start or join a team, and connect your agent. Each teammate does this on their own machine."
    >
      <div className="grid items-start gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <InstallTabs tabs={tabs} />
        <div className="grid items-start gap-6 md:grid-cols-2 xl:grid-cols-1">
          <div className="overflow-hidden rounded-2xl border border-code-line bg-code-bg text-code-ink">
            <p className="border-b border-code-line px-4 py-2.5 font-mono text-xs text-code-muted">
              add a teammate
            </p>
            <CodeLines snippet={teammate} />
          </div>
          <p className="text-sm leading-relaxed text-muted">
            You need Python 3.11 or newer on macOS, Linux or Windows. The <code>p2p</code> extra
            adds direct connections across networks; without it, the LAN, relays and shared folders
            still work. Every step is in the{" "}
            <a
              href={links.quickStart}
              target="_blank"
              rel="noreferrer"
              className="underline-accent"
            >
              quick start
            </a>
            .
          </p>
        </div>
      </div>
    </Section>
  );
}

export function ClosingCta() {
  return (
    <section aria-labelledby="cta-title" className="pb-24">
      <Container>
        <div className="relative overflow-hidden rounded-3xl bg-code-bg px-6 py-16 text-center text-code-ink sm:px-12 sm:py-20">
          <Mark
            id="cta-mark"
            className="pointer-events-none absolute -top-24 -right-24 size-80 opacity-25 motion-safe:animate-[spin_60s_linear_infinite]"
          />
          <h2
            id="cta-title"
            className="relative text-4xl font-semibold tracking-tight text-balance sm:text-6xl"
          >
            Go hand off <span className="em text-code-green">some work.</span>
          </h2>
          <p className="relative mx-auto mt-5 max-w-xl text-code-muted">
            Open source under MIT. Runs on macOS, Linux and Windows, with nothing to host.
          </p>
          <div className="relative mt-8 flex flex-wrap justify-center gap-3">
            <a
              href="#install"
              className="inline-flex h-11 items-center rounded-full bg-code-green px-5 text-sm font-medium text-[#0b1f17] transition-opacity hover:opacity-90"
            >
              Start building
            </a>
            <a
              href={links.repo}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-11 items-center gap-2 rounded-full border border-code-line px-5 text-sm font-medium text-code-ink transition-colors hover:border-code-green"
            >
              <GitHubIcon className="size-4" /> Star on GitHub
            </a>
          </div>
        </div>
      </Container>
    </section>
  );
}
