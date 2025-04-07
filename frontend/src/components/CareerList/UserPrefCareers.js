import React from 'react';

function UserPrefCareers({ skills }) {
  // for example, showing only jobs including "data"
  const userPref = skills.filter(skill => 
    skill.name.toLowerCase().includes("data")
  );

  return (
    <div>
      <h2>User Preferred Careers</h2>
      <ul>
        {userPref.map(skill => (
          <li key={skill.id}>{skill.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default UserPrefCareers;
