import axios from "~/axios";

export function fetchPlatformSettings() {
  return axios.get("/PlatformSettings/profile");
}

export function savePlatformSettings(payload) {
  return axios.put("/PlatformSettings/profile", payload);
}

export function generateDeployBundle(outputDir) {
  return axios.post("/PlatformSettings/generateDeployBundle", {
    output_dir: outputDir || "",
  });
}

export function importPlatformKeywords(formData) {
  return axios.post("/PlatformSettings/importKeywords", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

export function testNotification(payload) {
  return axios.post("/PlatformSettings/testNotification", payload);
}

export function runPlatformDiagnostics() {
  return axios.post("/PlatformSettings/runDiagnostics", {});
}
