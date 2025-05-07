import "@/app/globals.css"
import { Inter } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import { Navbar } from "@/components/navbar"
import Link from "next/link"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "VariantWise - Your Personalized Car Consultant",
  description:
    "Make informed car buying decisions with AI-powered insights on specific variants, real-world experiences, and personalized recommendations.",
    generator: 'v0.dev'
}

export const viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#000000" },
    { media: "(prefers-color-scheme: dark)", color: "#000000" },
  ],
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-primary-500`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange={false}>
          <Navbar />
          {children}
          <footer className="w-full border-t border-primary-400 py-6 bg-primary-500">
            <div className="container flex flex-col items-center justify-between gap-4 px-4 md:flex-row md:px-6">
              <p className="text-sm text-primary-200">© {new Date().getFullYear()} VariantWise. All rights reserved.</p>
              <nav className="flex gap-4 sm:gap-6">
                <Link href="/terms" className="text-sm text-primary-200 hover:underline hover:text-white">
                  Terms
                </Link>
                <Link href="/privacy" className="text-sm text-primary-200 hover:underline hover:text-white">
                  Privacy
                </Link>
                <Link href="/contact" className="text-sm text-primary-200 hover:underline hover:text-white">
                  Contact
                </Link>
              </nav>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  )
}



import './globals.css'