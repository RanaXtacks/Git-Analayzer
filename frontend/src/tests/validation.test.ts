// Unit test for GitHub repository URL validation logic

export function validateGitHubUrl(url: string): { valid: boolean; owner?: string; repo?: string; error?: string } {
  if (!url || !url.trim()) {
    return { valid: false, error: 'URL is required' };
  }
  const clean = url.trim();
  const match = clean.match(/^https?:\/\/(?:www\.)?github\.com\/([a-zA-Z0-9_.-]+)\/([a-zA-Z0-9_.-]+?)(?:\/)?(?:\.git)?$/);
  if (!match) {
    return { valid: false, error: 'Invalid GitHub repository URL format' };
  }
  return { valid: true, owner: match[1], repo: match[2] };
}

// Verification runner
(() => {
  const testCases = [
    { input: 'https://github.com/facebook/react', expectedValid: true, owner: 'facebook', repo: 'react' },
    { input: 'https://github.com/fastapi/fastapi/', expectedValid: true, owner: 'fastapi', repo: 'fastapi' },
    { input: 'https://github.com/torvalds/linux.git', expectedValid: true, owner: 'torvalds', repo: 'linux' },
    { input: 'https://gitlab.com/owner/repo', expectedValid: false },
    { input: 'https://github.com/facebook', expectedValid: false },
    { input: 'https://github.com/facebook/react/issues/1', expectedValid: false },
  ];

  for (const tc of testCases) {
    const res = validateGitHubUrl(tc.input);
    if (res.valid !== tc.expectedValid) {
      throw new Error(`Validation test failed for ${tc.input}: expected ${tc.expectedValid}, got ${res.valid}`);
    }
    if (tc.expectedValid && (res.owner !== tc.owner || res.repo !== tc.repo)) {
      throw new Error(`Owner/Repo mismatch for ${tc.input}: expected ${tc.owner}/${tc.repo}, got ${res.owner}/${res.repo}`);
    }
  }
  console.log('All frontend URL validation unit tests passed!');
})();
