# Going live: from "Claude preview" to a real, automated website

This is a one-time setup. After this, the site updates itself — you will
not need to come back to Claude to publish new counselling data (though
you're always welcome to, e.g. for a new feature or a bug fix). Budget
about 20-30 minutes, no coding required. Every step below tells you
exactly what to click.

## What you're setting up, in plain terms

Right now, the site only exists as a private preview link Claude hosts.
After this setup, three free services will work together:

1. **GitHub** — stores the website's code and data files, and keeps a
   full history of every change (this is your "never overwrite historical
   data" requirement, built in for free).
2. **GitHub Actions** — a free robot that runs on GitHub's own computers.
   Every 6 hours, it checks MCC's website for new documents, downloads
   and reads any new result PDFs, checks the numbers make sense, and
   updates the site — automatically, with no computer of yours needing to
   be on.
3. **GitHub Pages** — serves the actual website to visitors, for free,
   with your own domain (neetpghelp.com) once you point it there.

Nothing here costs money, and nothing requires you to type a command in a
terminal.

---

## Step 1 — Create a GitHub account

1. Go to **github.com** and click **Sign up** (top right).
2. Use your email (staranirban363@gmail.com or whichever you prefer),
   pick a username (e.g. `neetpghelp` or your own name), and set a
   password.
3. Verify your email when GitHub sends the confirmation link.

If you already have a GitHub account, skip to Step 2.

## Step 2 — Create the repository (the project's home on GitHub)

1. Once logged in, click the **+** icon at the top right, then **New
   repository**.
2. **Repository name:** `neetpg-mvp` (or any name you like).
3. Set it to **Private** for now — you can make it public later once
   you're ready (a private repo still deploys a public website fine).
4. Leave everything else as default. Click **Create repository**.

## Step 3 — Upload the project files

You'll upload the contents of the zip file Claude gave you.

1. First, unzip `neetpg-mvp.zip` on your computer (double-click it, or
   right-click → Extract).
2. On your new repository's GitHub page, click **uploading an existing
   file** (a link on the empty repo's page — if you don't see it, click
   **Add file → Upload files** instead).
3. Open the unzipped `neetpg-mvp` folder on your computer, select
   **everything inside it** (not the folder itself — go inside it first),
   and drag all of it into the browser window. Modern browsers (Chrome,
   Edge) will upload the folders too, keeping the structure intact.
4. Scroll down and click **Commit changes**.
5. **Double-check the `.github` folder made it.** After uploading, look
   at your repo's file list — you should see a folder literally named
   `.github`. GitHub sometimes hides dot-folders from drag-and-drop on
   older browsers. If it's missing:
   - Click **Add file → Create new file**.
   - In the "Name your file" box, type exactly:
     `.github/workflows/monitor.yml` (typing the slashes creates the
     folders automatically).
   - Open `.github/workflows/monitor.yml` from the unzipped folder on
     your computer in a text editor (Notepad, TextEdit), copy its
     contents, and paste them into GitHub's editor.
   - Click **Commit changes**.

## Step 4 — Turn on GitHub Actions (the automated checker)

1. Click the **Actions** tab on your repository.
2. GitHub may show a banner asking you to confirm you want to run
   workflows — click **I understand my workflows, go ahead and enable
   them**.
3. You should see a workflow called **MCC monitor**. Click it, then click
   **Run workflow** (top right) → **Run workflow** again to confirm.
4. Wait a minute or two, then refresh — you'll see a run appear. Click
   into it to watch it work. Green checkmark = it ran successfully.
   - This first run is the real test: it's the first time this code has
     ever touched the real mcc.nic.in from a machine with real internet
     access. If it fails, click into the failed step to see the error and
     send it to Claude — that's expected debugging, not a sign anything
     is fundamentally wrong.
5. From now on, this runs automatically every 6 hours, forever, for free
   (GitHub gives every account thousands of free minutes a month — this
   uses only a few minutes per run).

## Step 5 — Turn on GitHub Pages (make it a real website)

1. Click **Settings** (top of your repo) → **Pages** (left sidebar).
2. Under "Build and deployment", set **Source** to **GitHub Actions**
   (not "Deploy from a branch" — the MCC monitor workflow deploys the
   site itself, as its last step, so this just tells GitHub Pages to
   accept deployments from it).
3. Go back to the **Actions** tab and re-run the **MCC monitor** workflow
   once (same as Step 4) — its first run after this setting was flipped
   is what actually publishes the site.
4. Once that run finishes with a green checkmark, go back to **Settings →
   Pages** — you'll see a live URL like
   `https://yourusername.github.io/neetpg-mvp/`. Open it — that's your
   site, updating itself every 6 hours from here on.

## Step 6 — Point neetpghelp.com at it (optional, whenever you're ready)

You'll need to already own the domain neetpghelp.com (buy it from any
registrar — GoDaddy, Namecheap, Google Domains successor Squarespace
Domains, etc. — a `.com` is typically $10-15/year; this is the one cost
in this whole setup, and it's optional until you want the real domain
live).

1. In your domain registrar's dashboard, find **DNS settings** (sometimes
   called "Manage DNS" or "DNS records").
2. Add these two records (your registrar's exact wording may vary
   slightly — Claude can walk you through your specific registrar's
   screen if you share what you see):
   - Type `A`, Host `@`, pointing to GitHub Pages' IP addresses:
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
     `185.199.111.153` (add all four as separate A records).
   - Type `CNAME`, Host `www`, Value `yourusername.github.io`.
3. Back on GitHub: **Settings → Pages → Custom domain**, type
   `neetpghelp.com`, click **Save**. Wait for the green checkmark
   confirming it's verified (can take a few minutes to a few hours for
   DNS to update worldwide).
4. Tick **Enforce HTTPS** once it becomes available (usually within an
   hour) — this gives visitors the padlock/secure icon.

---

## What happens automatically from here

- Every 6 hours, GitHub checks MCC's three PG listing pages for anything
  new.
- A new notice or document is cataloged immediately (title, type, link) —
  this is naturally low-risk since nothing is reinterpreted, just linked.
- A new **result** document is downloaded, and the pipeline tries to read
  its seat/rank table automatically. If the numbers pass every validation
  check (no impossible ranks, no duplicate seats, categories and round
  names look right, nothing changed implausibly from a previous version),
  it's published to the Predictor automatically.
- If anything looks off, it is **not** published — instead, GitHub opens
  an **Issue** in your repository (visible under the **Issues** tab, and
  GitHub emails you about it), explaining exactly what looked wrong, so
  you or Claude can look at it before it goes live.
- Every change is a Git commit, so the full history of every dataset
  version is kept forever — nothing is ever silently overwritten.

## What you need to do from here

- **Nothing, day to day.** Check the **Issues** tab occasionally (or just
  wait for the email) for anything flagged for review.
- When something needs review, share the Issue link with Claude — that's
  the fastest way to get it looked at and fixed (e.g. a new document
  layout MCC hasn't used before, which needs a new small extractor
  written, same as the two we already have).
- If you want a state counselling authority added, or a faster/slower
  check interval, or the review process changed (e.g. always hold for
  your approval instead of auto-publishing), just ask Claude — those are
  all small, targeted changes to files already in this repo.

## If something goes wrong

Send Claude:
- The link to the failed Action run (Actions tab → click the red ✕ run),
  or
- The link to an Issue that got opened, or
- A screenshot of whatever screen you're stuck on.

Claude can read GitHub links directly and will tell you exactly what
changed and why.
