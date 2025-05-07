const express = require("express");
const router = express.Router();
const bcrypt = require("bcrypt");
const passport = require("passport");
const GoogleStrategy = require("passport-google-oauth20").Strategy;
const User = require("../models/user");
const autho = require("../middlewares/autho");

// --- Passport Google Strategy Configuration ---
passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: process.env.GOOGLE_CALLBACK_URL,
    },
    async (accessToken, refreshToken, profile, done) => {
      try {
        let user = await User.getUserByEmail(profile.emails[0].value);

        if (user) {
          return done(null, user);
        } else {
          // Create new user - passing null for password
          const newUserInfo = await User.createUser(
            profile.name.givenName || "GoogleUser",
            profile.name.familyName || "",
            profile.emails[0].value,
            null // Pass null for password for Google sign-up
          );
          // Fetch the newly created user to get their full details including ID
          user = await User.getUserByEmail(profile.emails[0].value);
          if (!user) {
            // Handle case where user creation seemed successful but fetch failed
            return done(
              new Error("Failed to retrieve newly created user."),
              null
            );
          }
          return done(null, user);
        }
      } catch (error) {
        console.error("Error in Google Strategy:", error); // Log the error
        return done(error, null);
      }
    }
  )
);

// --- Passport Session Serialization/Deserialization ---
passport.serializeUser((user, done) => {
  // Ensure user object has an 'id' property after creation/retrieval
  if (!user || typeof user.id === "undefined") {
    return done(
      new Error("User object or user ID is missing for serialization."),
      null
    );
  }
  done(null, user.id); // Store user ID in session
});

passport.deserializeUser(async (id, done) => {
  try {
    // Fetch user from DB using ID stored in session
    const user = await User.getUserById(id);
    if (!user) {
      return done(new Error("User not found during deserialization."), null);
    }
    done(null, user); // Pass the full user object
  } catch (error) {
    console.error("Error in deserializeUser:", error);
    done(error, null);
  }
});

router.get(
  "/auth/google",
  passport.authenticate("google", {
    scope: ["profile", "email"],
  })
);

// --- Google OAuth Routes ---
router.get(
  "/auth/google/callback",
  passport.authenticate("google", {
    failureRedirect: `${
      process.env.FRONTEND_URL || "http://localhost:3000"
    }/login?error=google_auth_failed`,
    failureMessage: true,
  }),
  async (req, res) => {
    try {
      if (!req.user) {
        console.error("Google auth callback success but req.user is missing.");
        return res.redirect(
          `${
            process.env.FRONTEND_URL || "http://localhost:3000"
          }/login?error=auth_error`
        );
      }

      // Save user to DB if not already present
      let user = await User.getUserByEmail(req.user.email);
      if (!user) {
        user = await User.createUser({
          email: req.user.email,
          first_name: req.user.first_name,
        });
      }

      // Set session
      req.session.user = {
        id: user.id,
        email: user.email,
        first_name: user.first_name,
      };

      console.log("User authenticated successfully:", req.session.user);

      // Wait for session to save before redirecting
      req.session.save(() => {
        res.redirect(
          `${process.env.FRONTEND_URL || "http://localhost:3000"}/dashboard`
        );
      });
    } catch (err) {
      console.error("Google callback error:", err);
      return res.redirect(
        `${
          process.env.FRONTEND_URL || "http://localhost:3000"
        }/login?error=server_error`
      );
    }
  }
);

router.post("/register", async (req, res) => {
  try {
    const { first_name, last_name, email, password } = req.body;
    await User.createUser(first_name, last_name, email, password);
    res.json({ success: true, message: "User registered" });
  } catch (error) {
    console.error("Registration error:", error);
    res.status(500).json({ success: false, message: "Registration failed" });
  }
});

router.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.getUserByEmail(email);
    if (!user)
      return res
        .status(401)
        .json({ success: false, message: "Invalid credentials" });

    const match = await bcrypt.compare(password, user.password);
    if (!match)
      return res
        .status(401)
        .json({ success: false, message: "Invalid credentials" });

    req.session.user = {
      id: user.id,
      email: user.email,
      first_name: user.first_name,
    };

    req.session.save(() => {
      // Tell browser to save cookie now
      res.cookie("connect.sid", req.sessionID, {
        httpOnly: true,
        sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
        secure: process.env.NODE_ENV === "production",
      });

      res.json({
        success: true,
        message: "Logged in",
        user: { first_name: user.first_name },
      });
    });
  } catch (error) {
    console.error("Login error:", error);
    res.status(500).json({ success: false, message: "Login failed" });
  }
});

router.post("/logout", autho, (req, res) => {
  req.session.destroy(() => {
    res.json({ success: true, message: "Logged out" });
  });
});

router.get("/dashboard", autho, (req, res) => {
  res.json({ success: true, message: "Welcome to your dashboard" });
});

router.get("/me", autho, (req, res) => {
  res.json({ user: req.session.user });
});

module.exports = router;
