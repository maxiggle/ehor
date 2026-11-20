import { Header } from "@/app/_components/header";
import { Platforms, Tools } from "@/app/_sections/features";
import { Footer } from "@/app/_sections/footer";
import { Hero } from "@/app/_sections/hero";
import { ClosingCta, Install } from "@/app/_sections/install";
import { Messages } from "@/app/_sections/messages";
import { Products } from "@/app/_sections/products";
import { Security } from "@/app/_sections/security";

export default function Home() {
  return (
    <>
      <Header />
      <main id="main">
        <Hero />
        <Messages />
        <Tools />
        <Security />
        <Platforms />
        <Install />
        <Products />
        <ClosingCta />
      </main>
      <Footer />
    </>
  );
}
