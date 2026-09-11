// Runs INSIDE the active frontend's Node container; no host Node is required.
const mode = process.argv[2];
const fields = process.argv.slice(3);
const checks = [];
for (let i = 0; i < fields.length; i += 5) {
  const [name, ready, expectedBody, health, representative] = fields.slice(i, i + 5);
  checks.push({ name: `${name} readiness`, url: ready, body: expectedBody });
  if (mode === "smoke") {
    if (health !== "none") checks.push({ name: `${name} health`, url: health, body: "none" });
    checks.push({ name: `${name} representative GET`, url: representative, body: "none" });
  }
}
async function check(item) {
  let response;
  try { response = await fetch(item.url, { signal: AbortSignal.timeout(5000) }); }
  catch (error) { throw new Error(`${item.name}: ${error.message} (${item.url})`); }
  if (response.status !== 200) throw new Error(`${item.name}: HTTP ${response.status} (${item.url})`);
  if (item.body !== "none" && (await response.text()).trim() !== item.body)
    throw new Error(`${item.name}: unexpected readiness body`);
}
(async () => {
  if (!["readiness", "smoke"].includes(mode) || !checks.length || fields.length % 5)
    throw new Error("Invalid or empty active probe contract");
  const deadline = Date.now() + (mode === "readiness" ? 120000 : 0);
  for (;;) {
    const outcomes = await Promise.allSettled(checks.map(check));
    const failures = outcomes.filter(result => result.status === "rejected");
    if (!failures.length) break;
    if (Date.now() >= deadline) throw new Error(failures.map(result => result.reason.message).join("\n"));
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  for (const item of checks) console.log(`PASS ${item.name}: ${item.url}`);
  if (mode === "smoke") console.log("Transport/readiness checks only; this does not prove a browser-to-backend feature flow.");
})().catch(error => { console.error(error.message); process.exitCode = 1; });
