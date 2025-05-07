"use client"

import * as React from "react"
import Link from "next/link"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { User } from "lucide-react"
import { MobileNav } from "@/components/mobile-nav"
import { usePathname } from "next/navigation"
import axios from "axios"

export function Navbar() {
  const { setTheme, theme } = useTheme()
  const [isScrolled, setIsScrolled] = React.useState(false)
  const [user, setUser] = React.useState(null)
  const pathname = usePathname()

  const isAuthPage = pathname === "/signin" || pathname === "/signup"

  // Detect scroll
  React.useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10)
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  // ✨ Refetch /api/me every time path changes (like after login redirect)
  React.useEffect(() => {
    const timeout = setTimeout(() => {
      axios
        .get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/me`, { withCredentials: true })
        .then((res) => {
          setUser(res.data.user)
          console.log("✅ User loaded from /me:", res.data.user)
        })
        .catch((err) => {
          setUser(null)
          console.log("❌ /me error:", err.response?.data || err.message)
        })
    }, 300) // slight delay to let session cookie settle

    return () => clearTimeout(timeout)
  }, [pathname]) // ⬅️ re-run every time the path changes

  const handleLogout = async () => {
    await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/logout`, {}, { withCredentials: true })
    setUser(null)
    window.location.href = "/signin"
  }

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-200 ${
        isScrolled
          ? "bg-primary-500/95 backdrop-blur supports-[backdrop-filter]:bg-primary-500/60 border-b border-primary-400"
          : "bg-primary-500"
      }`}
    >
      <div className="container flex h-16 items-center justify-between px-4 md:px-6">
        <div className="flex items-center">
          <MobileNav />
          <Link href="/" className="flex items-center gap-2 ml-2 md:ml-0">
            <span className="text-xl font-bold interactive-text text-white">
              <span className="text-primary-100">Variant</span>Wise
            </span>
          </Link>
        </div>

        <nav className="hidden gap-6 md:flex">
          <Link href="/" className="text-sm font-medium transition-colors hover:text-primary-200 text-white">
            Home
          </Link>
          <Link href="/dashboard" className="text-sm font-medium transition-colors hover:text-primary-200 text-white">
            Dashboard
          </Link>
          <Link href="/consultant" className="text-sm font-medium transition-colors hover:text-primary-200 text-white">
            Consultation
          </Link>
        </nav>

        <div className="flex items-center gap-2">
          {!isAuthPage && (
            <>
              <Button variant="ghost" size="icon" className="rounded-full" asChild>
                <Link href="/dashboard">
                  <User className="h-5 w-5 text-white" />
                  <span className="sr-only">Profile</span>
                </Link>
              </Button>

              {user ? (
                <>
                  <span className="text-white text-sm hidden md:inline">Hi, {user.first_name}</span>
                  <Button
                    className="hidden md:flex bg-red-500 hover:bg-red-600 text-white border border-red-400"
                    onClick={handleLogout}
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <Button
                  className="hidden md:flex bg-black hover:bg-primary-400 text-white border border-primary-300"
                  asChild
                >
                  <Link href="/signin">Sign In</Link>
                </Button>
              )}
            </>
          )}
        </div>
      </div>
    </header>
  )
}
