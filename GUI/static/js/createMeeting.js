document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("create-meeting-modal");
  const btn = document.getElementById("create-meeting-btn");
  const span = document.getElementsByClassName("close")[0];
  const form = document.getElementById("create-meeting-form");
  const userId = "zcxsTyXdQZGhk5VLjLPyjw"; // Replace with the actual user ID
  const accessToken = "your_access_token"; // Replace with the actual access token

  btn.onclick = function () {
    modal.style.display = "block";
  };

  span.onclick = function () {
    modal.style.display = "none";
  };

  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };

  form.onsubmit = async function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const data = {
      topic: formData.get("topic"),
      start_time: formData.get("start_time"),
      duration: parseInt(formData.get("duration")),
      timezone: formData.get("timezone"),
      agenda: formData.get("agenda"),
      type: parseInt(formData.get("type")), // Include the type field
      invitees: formData
        .get("invitees")
        .split(",")
        .map((email) => email.trim()),
    };

    try {
      const response = await fetch("/meetings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const result = await response.json();
        alert("Cuộc họp đã được tạo thành công!");
        modal.style.display = "none";
      } else {
        const error = await response.json();
        alert("Lỗi: " + error.detail);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Đã xảy ra lỗi khi tạo cuộc họp.");
    }
  };
  async function fetchUpcomingMeetings() {
    try {
      const response = await fetch(`/meetings/users/${userId}/upcoming`, {
        method: "GET",
      });
      if (response.ok) {
        const meetings = await response.json();
        console.log(meetings);
        populateMeetingTable(meetings);
      } else {
        const error = await response.json();
        console.error("Error fetching meetings:", error);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  async function fetchCurrentMeetings() {
    try {
      const response = await fetch(`/meetings/users/${userId}/live`, {
        method: "GET",
      });

      if (response.ok) {
        const meetings = await response.json();
        currentMeetingTable(meetings);
      } else {
        const error = await response.json();
        console.error("Error fetching meetings:", error);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  function populateMeetingTable(meetings) {
    const tbody = document
      .getElementById("upcoming-meetings-table")
      .getElementsByTagName("tbody")[0];
    tbody.innerHTML = ""; // Clear existing rows
    meetings.forEach((meeting) => {
      if(Date.now() > new Date(meeting.start_time).getTime()) return;
      const row = tbody.insertRow();
      row.insertCell(0).innerText = meeting.topic;
      let startTime = new Date(meeting.start_time);
      startTime.setHours(startTime.getHours() + 7);
      let formattedDate = startTime.toISOString();
      row.insertCell(1).innerText = formattedDate;
      row.insertCell(2).innerText = meeting.duration;
      row.insertCell(
        3
      ).innerHTML = `<button onclick="manageMeeting('${meeting.id}')">Quản lý</button>`;
      row.insertCell(
        4
      ).innerHTML = `<button onclick="joinMeeting('${meeting.join_url}')">Tham gia</button>`;
    });
  }

  function currentMeetingTable(meetings) {
    const tbody = document
      .getElementById("current-meetings-table")
      .getElementsByTagName("tbody")[0];
    tbody.innerHTML = ""; // Clear existing rows
    const now = new Date();
    meetings.forEach((meeting) => {
      const row = tbody.insertRow();
      row.insertCell(0).innerText = meeting.topic;
      let startTime = new Date(meeting.start_time);
      startTime.setHours(startTime.getHours() + 7);
      let formattedDate = startTime.toISOString();
      row.insertCell(1).innerText = formattedDate;
      row.insertCell(2).innerText = meeting.duration;
      row.insertCell(
        3
      ).innerHTML = `<button onclick="manageMeeting('${meeting.id}')">Quản lý</button>`;
      row.insertCell(
        4
      ).innerHTML = `<button onclick="joinMeeting('${meeting.join_url}')">Tham gia</button>`;
    });
  }

  fetchUpcomingMeetings();
  fetchCurrentMeetings();
});

function manageMeeting(meetingId) {
  alert(`Quản lý cuộc họp: ${meetingId}`);
  // Add your management logic here
}

function joinMeeting(joinUrl) {
  // redirect to the meeting page by another tab
  window.open(joinUrl, "_blank");
}
