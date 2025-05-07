"use client"

import * as React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Menu } from "lucide-react"
import { usePathname } from "next/navigation"

export function MobileNav() {
  const [open, setOpen] = React.useState(false)
  const pathname = usePathname()

  // Check if user is on auth pages
  const isAuthPage = pathname === "/signin" || pathname === "/signup"

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden text-white">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="flex flex-col bg-primary-400 border-primary-300">
        <nav className="flex flex-col gap-4 mt-8">
          <Link
            href="/"
            className="text-lg font-medium transition-colors hover:text-primary-100 text-white"
            onClick={() => setOpen(false)}
          >
            Home
          </Link>
          <Link
            href="/features"
            className="text-lg font-medium transition-colors hover:text-primary-100 text-white"
            onClick={() => setOpen(false)}
          >
            Features
          </Link>
          <Link
            href="/pricing"
            className="text-lg font-medium transition-colors hover:text-primary-100 text-white"
            onClick={() => setOpen(false)}
          >
            Pricing
          </Link>
          <Link
            href="/about"
            className="text-lg font-medium transition-colors hover:text-primary-100 text-white"
            onClick={() => setOpen(false)}
          >
            About
          </Link>
          <Link
            href="/dashboard"
            className="text-lg font-medium transition-colors hover:text-primary-100 text-white"
            onClick={() => setOpen(false)}
          >
            Dashboard
          </Link>
          <Link
            href="/consultant"
            className="text-lg font-medium transition-colors hover:text-primary-100 text-white"
            onClick={() => setOpen(false)}
          >
            Consultant
          </Link>
        </nav>
        <div className="mt-auto mb-8">
          {!isAuthPage && (
            <div className="space-y-2">
              <Link href="/signin">
                <Button
                  className="w-full bg-black hover:bg-primary-500 text-white border border-primary-300"
                  onClick={() => setOpen(false)}
                >
                  Sign In
                </Button>
              </Link>
              <Link href="/signup">
                <Button
                  variant="outline"
                  className="w-full border-primary-300 text-white hover:bg-primary-500"
                  onClick={() => setOpen(false)}
                >
                  Sign Up
                </Button>
              </Link>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}

