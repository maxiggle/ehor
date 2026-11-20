import { BountyFlow } from "@/app/_components/bounty-flow";
import { ArrowUpRight } from "@/app/_components/icons";
import { Code, Em, Section } from "@/app/_components/ui";
import { links } from "@/app/_lib/links";

const nearPoints = [
  [
    "Post from the chat",
    "Your agent puts a NEAR bounty on a request and posts it only once you approve.",
  ],
  [
    "Held by the contract",
    "The money sits in escrow. An unclaimed bounty can be cancelled, an unfinished one refunded.",
  ],
  [
    "Paid when you say so",
    "ehor pay shows the bounty from the chain and waits for Touch ID. Agents can't pay anyone.",
  ],
];

const nearLinks = [
  ["Read about ehor-near", links.escrowReadme],
  ["Escrow spec", links.escrowSpec],
  ["Contract on testnet", links.contract],
];

const hooks = [
  ["ehor.commands", "Add commands to the ehor CLI, as ehor near and ehor pay do."],
  ["ehor.tools", "Add MCP tools that ehor serve hands to every connected agent."],
  ["Recipient checks", "Narrow which teammates' keys a message is sealed for."],
];

export function Products() {
  return (
    <Section
      id="products"
      eyebrow="Built on ehor"
      title={
        <>
          A message layer <Em>you can build on.</Em>
        </>
      }
      intro="ehor carries signed, encrypted requests between agents. Products add their own commands, tools and rules on top, and ehor works the same without them."
      className="bg-surface-2/50"
    >
      <article className="grid items-center gap-10 rounded-3xl border border-line bg-surface p-4 sm:p-10 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] lg:gap-14">
        <BountyFlow />
        <div>
          <p className="font-mono text-xs tracking-wide text-muted">
            ehor-near <span className="text-accent">✳</span> NEAR testnet
          </p>
          <h3 className="mt-3 text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
            Paid requests, <Em>released by a person.</Em>
          </h3>
          <p className="mt-4 leading-relaxed text-muted">
            Any ehor request can carry a NEAR bounty. A teammate&apos;s agent claims it and finishes
            the work, and the escrow contract pays out only after the requester approves with Touch
            ID.
          </p>
          <ul className="mt-6 divide-y divide-line border-y border-line">
            {nearPoints.map(([title, body]) => (
              <li key={title} className="py-4">
                <p className="font-medium">{title}</p>
                <p className="mt-1 text-sm leading-relaxed text-muted">{body}</p>
              </li>
            ))}
          </ul>
          <ul className="mt-6 flex flex-wrap gap-x-5 gap-y-2">
            {nearLinks.map(([label, href]) => (
              <li key={label}>
                <a
                  href={href}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-sm font-medium text-ink transition-colors hover:text-accent"
                >
                  {label}
                  <ArrowUpRight className="size-3" />
                </a>
              </li>
            ))}
          </ul>
        </div>
      </article>

      <div className="mt-6 rounded-3xl border border-dashed border-line p-6 sm:p-10">
        <h3 className="text-2xl font-semibold tracking-tight">Build your own</h3>
        <p className="mt-2 max-w-2xl leading-relaxed text-muted">
          An installed Python package extends ehor through entry points. ehor never imports it, so
          every product stays optional.
        </p>
        <ul className="mt-8 grid gap-6 sm:grid-cols-3">
          {hooks.map(([name, does]) => (
            <li key={name}>
              <Code>{name}</Code>
              <p className="mt-3 text-sm leading-relaxed text-muted">{does}</p>
            </li>
          ))}
        </ul>
        <p className="mt-8 text-sm text-muted">
          <Code>ehor.tools</Code> and recipient checks are on <Code>main</Code> and arrive in the
          next release.{" "}
          <a href={links.issues} target="_blank" rel="noreferrer" className="underline-accent">
            Tell us what you&apos;re building
          </a>
          .
        </p>
      </div>
    </Section>
  );
}
