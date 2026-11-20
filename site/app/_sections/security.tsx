import { Em, Section } from "@/app/_components/ui";

const invariants = [
  [
    "No message can change the team.",
    "Roster changes are CLI commands signed by an admin. MCP can't reach them.",
  ],
  [
    "A teammate's message is data.",
    "Tool results label it as written by a named person. Nothing acts on it by itself.",
  ],
  [
    "Every entry is checked first.",
    "Signature, roster membership, prev chain, fork check and dedupe, before anything is stored.",
  ],
  [
    "Stored entries never change.",
    "Each device's log is append-only. Nothing edits or deletes an entry once it is stored.",
  ],
  ["Relays carry only ciphertext.", "They see who wrote an entry and when, never what it says."],
  [
    "Removing someone cuts them off.",
    "There is no shared team key, so they can't read the very next message.",
  ],
  [
    "Signing keys stay in hardware.",
    "A Secure Enclave or TPM key never leaves its chip, and nothing logs key material.",
  ],
  [
    "A stolen laptop can't change the roster.",
    "With a security key enrolled, every roster change needs a physical touch.",
  ],
  [
    "Notifications never run teammate text.",
    "A teammate's summary is passed as data, cut to one line of plain text.",
  ],
];

export function Security() {
  return (
    <Section
      id="security"
      eyebrow="Security model"
      title={
        <>
          Built for <Em>untrusted</Em> input.
        </>
      }
      intro="An agent that reads a teammate's message can be talked into what the message says. ehor keeps that message as data and keeps the team out of its reach. These hold by design, and tests enforce them."
    >
      <ol className="grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-3">
        {invariants.map(([title, body], i) => (
          <li key={title} className="bg-surface p-6 sm:max-lg:last:col-span-2">
            <span className="font-mono text-xs text-accent">{String(i + 1).padStart(2, "0")}</span>
            <h3 className="mt-3 font-semibold tracking-tight">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{body}</p>
          </li>
        ))}
      </ol>
    </Section>
  );
}
