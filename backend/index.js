const express = require("express");
const session = require("express-session");
const cors = require("cors");
const passport = require("passport");
const app = express();
require("dotenv").config();
require("./db/config");
const authRoutes = require("./routes/auth");

const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:3000";
const SESSION_SECRET = process.env.Secret_Key || "fallback-secret";
const IS_PROD = process.env.NODE_ENV === "production";

// Trust proxy needed for secure cookies to work behind a proxy
if (IS_PROD) {
  app.set("trust proxy", 1);
}

// --- CORS Setup (allow frontend to send cookies) ---
app.use(
  cors({
    origin: FRONTEND_URL,
    credentials: true,
  })
);

// --- JSON Parser ---
app.use(express.json());

// --- Session Setup ---
app.use(
  session({
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: IS_PROD,
      sameSite: IS_PROD ? "none" : "lax",
    },
  })
);

// --- Passport Initialization ---
app.use(passport.initialize());
app.use(passport.session());

// --- Route ---
app.use("/api", authRoutes);

// --- Server Start ---
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
