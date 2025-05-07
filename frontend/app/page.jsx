"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { MoveRight } from "lucide-react"
import Image from "next/image"
import { useEffect , useState } from "react"
import { useRouter } from "next/navigation"
import axios from "axios"

export default function LandingPage() {


  return (
    <div className="flex min-h-screen flex-col  bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-700 via-black to-black text-white ">
      <main className="flex-1">
      <section className="w-full h-[90vh]">
  <div className="container px-4 md:px-6 h-full flex items-center justify-center">
    <div className="flex flex-col items-center text-center space-y-10">
      <div className="space-y-8 text-center px-4 font-sans">
        <h1 className="text-7xl font-black tracking-tight text-white leading-tight">
          <span className="text-primary-100 drop-shadow-md">VariantWise</span>
        </h1>

        <h2 className="text-xl font-bold text-primary-200 leading-relaxed">
          Your Personalized Car Consultant
        </h2>

        <p className="mx-auto text-justify max-w-[730px] text-primary-200 md:text-xl leading-loose font-normal">
          Discover the easiest way to find your perfect car. With AI-powered insights, real-world reviews,
          and expert recommendations, VariantWise helps you choose the <strong>right variant</strong> effortlessly. Join us and make confident car buying decisions today!
        </p>
      </div>

      <div className="flex flex-col gap-3 min-[400px]:flex-row">
        <Link href="/dashboard">
          <Button
            size="lg"
            className="w-full min-[400px]:w-auto bg-black hover:bg-primary-400 text-white border border-primary-300"
          >
            Dashboard
            <MoveRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
        <Link href="/consultant">
          <Button
            size="lg"
            variant="outline"
            className="w-full min-[400px]:w-auto border-primary-300 text-white hover:bg-primary-400"
          >
            AI Consultant
          </Button>
        </Link>
      </div>
    </div>
  </div>
</section>

        <section className="w-full py-12 md:py-24 lg:py-32 ">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-3 lg:gap-12">
              <div className="flex flex-col justify-center space-y-4">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-black text-white">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6"
                  >
                    <path d="M3 17h4v1a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-1h2v1a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-1h4" />
                    <path d="M14 7h-4" />
                    <path d="M19 17H5" />
                    <path d="M21 9a2 2 0 0 0-2-2h-2l-2-3h-6L7 7H5a2 2 0 0 0-2 2v8h18V9Z" />
                  </svg>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-white">Variant-Specific Insights</h3>
                  <p className="text-primary-200">
                    Get detailed information about specific car variants, not just the top-tier models.
                  </p>
                </div>
              </div>
              <div className="flex flex-col justify-center space-y-4">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-black text-white">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6"
                  >
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-white">Real-World Experiences</h3>
                  <p className="text-primary-200">
                    Access aggregated insights from real owners about comfort, quality, and driving feel.
                  </p>
                </div>
              </div>
              <div className="flex flex-col justify-center space-y-4">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-black text-white">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6"
                  >
                    <path d="M20 17a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2" />
                    <path d="M14 13V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v6" />
                    <path d="M12 19a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2" />
                    <path d="M20 19h-8" />
                  </svg>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-white">Personalized Recommendations</h3>
                  <p className="text-primary-200">
                    Get AI-powered car recommendations based on your specific needs and preferences.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="w-full py-12 md:py-24 lg:py-32 ">
          <div className="container px-4 md:px-6">
            <div className="grid items-center gap-6 lg:grid-cols-2 lg:gap-12">
              <div className="space-y-4">
                <div className="inline-flex items-center rounded-lg bg-primary-400 px-3 py-1 text-sm">
                  <span className="font-medium text-white">How It Works</span>
                </div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl/tight text-white">
                  Make informed car buying decisions with VariantWise
                </h2>
                <p className="max-w-[600px] text-primary-200 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Our AI-powered platform aggregates technical specifications and real-life experience factors to help
                  you find the perfect car variant for your needs.
                </p>
                <div className="flex flex-col gap-2 min-[400px]:flex-row">
                  <Link href="/consultant">
                    <Button
                      size="lg"
                      className="w-full min-[400px]:w-auto bg-black hover:bg-primary-400 text-white border border-primary-300"
                    >
                      Try AI Consultant
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="flex justify-center">
                <div className="relative w-full max-w-[600px] overflow-hidden rounded-xl shadow-lg">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary-400/20 to-black/20"></div>
                  <Image
                    src="/placeholder.svg?height=400&width=600"
                    width={600}
                    height={400}
                    alt="VariantWise Dashboard Preview"
                    className="aspect-video overflow-hidden rounded-xl object-cover object-center"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="w-full py-12 md:py-24 lg:py-32 text-white">
          <div className="container grid items-center justify-center gap-4 px-4 text-center md:px-6">
            <div className="space-y-3">
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl/tight">Ready to find your perfect car?</h2>
              <p className="mx-auto max-w-[600px] text-primary-200 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Join VariantWise today and experience a personalized car buying journey.
              </p>
            </div>
            <div className="mx-auto w-full max-w-sm space-y-2">
              <form className="flex space-x-2">
                <input
                  className="flex h-10 w-full rounded-md border border-primary-300 bg-primary-400/90 px-3 py-2 text-sm text-white ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-primary-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-300 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="Enter your email"
                  type="email"
                />
                <Button type="submit" className="bg-black text-white hover:bg-primary-400 border border-primary-300">
                  Subscribe
                </Button>
              </form>
              <p className="text-xs text-primary-200">
                Sign up to get notified when we launch.{" "}
                <Link href="/terms" className="underline underline-offset-2 hover:text-white">
                  Terms & Conditions
                </Link>
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

