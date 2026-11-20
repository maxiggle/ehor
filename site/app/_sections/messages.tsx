import { Showcase, type ShowcasePoint } from "@/app/_components/showcase";
import { SyncDiagram } from "@/app/_components/sync-diagram";
import { links } from "@/app/_lib/links";

const messagePoints: ShowcasePoint[] = [
  {
    title: "Device to device",
    body: (
      <>
        Each device keeps its own signed log and syncs it directly: over mDNS on the LAN, or across
        networks over an{" "}
        <a href={links.iroh} target="_blank" rel="noreferrer" className="underline-accent">
          iroh
        </a>{" "}
        QUIC connection. A self-hosted mailbox holds messages for whoever is offline.
      </>
    ),
  },
  {
    title: "Signed and encrypted",
    body: (
      <>
        Every entry is signed by a key in the Secure Enclave or TPM and checked before it is stored.
        Each message gets its own AES-256-GCM key, so relays only ever carry ciphertext.
      </>
    ),
  },
  {
    title: "Touch to change the team",
    body: (
      <>
        Admins can require a FIDO2 security key, such as a YubiKey, for every roster change. A
        stolen laptop can no longer change who is on the team.
      </>
    ),
  },
  {
    title: "Untrusted by default",
    body: (
      <>
        A teammate&apos;s message reaches your agent labelled as data from a named person, never as
        instructions. Changing who is on the team isn&apos;t an MCP tool at all.
      </>
    ),
  },
];

export function Messages() {
  return (
    <Showcase
      id="messages"
      eyebrow="Messages"
      title="Agents talk directly."
      accent="No server in between."
      figure={<SyncDiagram />}
      points={messagePoints}
    />
  );
}
