Yes, you can retrieve a GitHub user's contributions across all their projects using the **GitHub REST API** or **GraphQL API**, but there are limitations due to API constraints and GitHub's data structure. Here's a step-by-step approach:

---

### 1. **Get All Repositories the User Contributed To**
   - Use the **Search API** to find repositories where the user committed code:
     ```http
     GET /search/commits?q=author:{username}
     ```
     Example:  
     `curl -H "Authorization: token YOUR_TOKEN" "https://api.github.com/search/commits?q=author:octocat"`

   - **Limitations**:  
     - Only returns the first 1,000 results (pagination won't help beyond this).
     - Results are limited to the past year due to GitHub's search index.

---

### 2. **Get Repository List for the User**
   - **Owned repositories**:  
     ```http
     GET /users/{username}/repos
     ```
   - **Repositories they contribute to** (non-owned):  
     Use the **Events API** to find `PushEvent` or `PullRequestEvent` activity:
     ```http
     GET /users/{username}/events
     ```
     Filter events to extract unique repository names.

   - **Limitations**:  
     - Events are only retained for 90 days.
     - Does not cover all contributions (e.g., issues, reviews).

---

### 3. **Get Commit/Contribution Stats per Repository**
   For each repository found:
   - **Commit history**:  
     ```http
     GET /repos/{owner}/{repo}/commits?author={username}
     ```
   - **Contribution stats** (additions/deletions):  
     ```http
     GET /repos/{owner}/{repo}/stats/contributors
     ```
     Look for the user in the response.

   - **Note**: Stats are cached and may take time to compute.

---

### 4. **Aggregate All Data**
   Combine results from all repositories to get totals:
   - **Total commits**  
   - **Total lines changed** (additions/deletions)  
   - **Repositories contributed to**

---

### Limitations & Workarounds
1. **API Rate Limits**:  
   - Unauthenticated: 60 requests/hour.  
   - Authenticated: 5,000 requests/hour (use a [personal access token](https://github.com/settings/tokens)).  
   - For large-scale scraping, use pagination and parallel requests cautiously.

2. **Incomplete Data**:  
   - GitHub does not expose a single endpoint for "all contributions".  
   - Private repository data requires authorization and won’t appear in public APIs unless you have access.

3. **Tool Alternatives**:  
   - **[GitHub Contributions Viewer](https://github-contributions.vercel.app)**: Browser-based tool.  
   - **[githubstats](https://githubstats.com)**: Third-party dashboards.  
   - **[Octokit](https://github.com/octokit)**: Libraries to automate API calls (JavaScript/Ruby).

---

### Example GraphQL Query
For more efficient data fetching, use GraphQL (avoids over-fetching):
```graphql
query {
  user(login: "username") {
    contributionsCollection {
      totalCommitContributions
      totalRepositoriesWithContributedCommits
      commitContributionsByRepository {
        repository {
          nameWithOwner
        }
        contributions {
          totalCount
        }
      }
    }
    repositoriesContributedTo(first: 100) {
      nodes {
        nameWithOwner
      }
    }
  }
}
```
Run this via the [GraphQL Explorer](https://docs.github.com/en/graphql/overview/explorer).

---

### Summary
- **Feasible?** Yes, but requires aggregating data from multiple endpoints.  
- **Complete?** No—private repos, >1-year-old data, and >1,000 results are truncated.  
- **Recommended**: Use the [`contributionsCollection`](https://docs.github.com/en/graphql/reference/objects#contributionscollection) in GraphQL for the most efficient summary of contributions.

For large-scale analysis, consider GitHub's [Data Exports](https://docs.github.com/en/enterprise-cloud@latest/migrations/exporting-migration-data/about-migration-data-export) (Enterprise only).
