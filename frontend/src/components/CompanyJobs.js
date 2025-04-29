import { useParams, Link } from 'react-router-dom';
import { useEffect, useState } from 'react';

export default function CompanyJobs() {
  const { companyId } = useParams();
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    fetch(`/api/company/${companyId}/jobs/`)
      .then(r => r.json())
      .then(setJobs)
      .catch(console.error);
  }, [companyId]);

  return (
    <div>
      <h1>Jobs for company #{companyId}</h1>
      {jobs.length === 0
        ? <p>No jobs found.</p>
        : jobs.map(j => (
            <div key={j.id}>
              <Link to={`/job/${j.id}`}>{j.title}</Link>
              <span> — {j.posting_date}</span>
            </div>
          ))
      }
    </div>
  );
}
