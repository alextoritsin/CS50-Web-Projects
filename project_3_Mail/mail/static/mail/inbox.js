document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Send new email
  document.querySelector('#compose-form').addEventListener('submit', send_email);
  
  // Archive button functionality
  document.querySelector('.archive').addEventListener('click', change_archive);

  // Reply button functionality
  document.querySelector('.reply').addEventListener('click', load_reply);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-content').style.display = 'none';

  // Hide error div
  let error = document.querySelector('#error');
  error.innerHTML = '';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


function send_email(e) {
  // Sending email after form submitting
  fetch('/emails', {
    method: "POST",
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value,
    })
  })
    .then(response => response.json())
    .then(result => {
      if (result.error) {
        error.innerHTML = result.error;
      } else if (result.message) {
        load_mailbox('sent');
      }
    })
    e.preventDefault();
}


function change_archive() {
  
  // Change achive status
  let button = document.querySelector('.archive')
  fetch(`/emails/${button.dataset.email}`)
    .then(response => response.json())
    .then(email => {
      fetch(`/emails/${email.id}`, {
        method: "PUT",
        body: JSON.stringify({
          archived: (!email.archived)
        })
      })
        .then(function () {
          load_mailbox('inbox');
        })
    })
}


function load_email_content(email, mailbox) {

  // Mark email as read
  if (!email.read) {
    fetch(`/emails/${email.id}`, {
      method: "PUT",
      body: JSON.stringify({
        read: true
      })
    })
  }

  // Archive mail button
  const archive = document.querySelector('.archive')
  const reply_btn = document.querySelector('.reply');
  reply_btn.dataset.reply = email.id;
  if (mailbox == 'sent') {
    archive.style.display = 'none';
  } else {
    archive.style.display = 'block';
    archive.innerHTML = (email.archived) ? 'Unarchive' : 'Archive';
    archive.dataset.email = email.id;
  }

  // Load email content
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-content').style.display = 'block';
  const header = document.querySelector('.header');
  header.innerHTML = `<div><b>From:</b> ${email.sender}</div>` +
    `<div><b>To:</b> ${email.recipients.join(', ')}</div>` +
    `<div><b>Subject:</b> ${email.subject}</div>` +
    `<div><b>Timestamp:</b> ${email.timestamp}</div>`;
  document.querySelector('.content').innerHTML = `${email.body}`;
}


function load_email_row(email, mailbox, container) {
  // Check email existance
  const div_row = document.getElementById(`${email.id}`);
  if (!div_row) {
    // Create new div and add click event
    const div_row = document.createElement('div');
    div_row.className = 'row';
    div_row.id = `${email.id}`
    div_row.addEventListener('click', function () {
      load_email_content(email, mailbox);
    })

    // Style element color
    if (email.read) {
      div_row.style.backgroundColor = '#dbdbdb6e';
    } else {
      div_row.style.backgroundColor = 'white';
    }
    container.append(div_row);

    // Create divs and fill them with email data
    let data = [
      (mailbox != 'sent') ? `${email.sender}` : `To Whom: ${email.recipients.join(', ')}`,
      email.subject,
      email.timestamp,
    ];

    for (const [index, value] of data.entries()) {
      let div_col = document.createElement('div');
      div_col.className = 'col-4';
      div_col.innerHTML = value;
      div_col.dataset.email = `${index + 1}`;
      div_row.append(div_col);
    }
  }
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-content').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show the mailbox content
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      const container = document.querySelector('#emails-view')
      if (emails.error) {
        container.append(emails.error)
      } else {
        emails.forEach(email => {
          load_email_row(email, mailbox, container)
        });
      }
    })
}


function load_reply() {

  // Get elements and fetch email data
  const user = document.querySelector('h2').innerHTML;
  const reply_btn = document.querySelector('.reply');
  const form = document.querySelector('form');
  fetch(`/emails/${reply_btn.dataset.reply}`)
    .then(response => response.json())
    .then(email => {
      const check_user = (user == email.sender);
      document.querySelector('#compose-recipients').value = check_user ? email.recipients.join(', ') : email.sender;
      document.querySelector('#compose-subject').value = (email.subject.startsWith("Re:")) ? email.subject : ("Re: " + email.subject);
      document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp} ${email.sender} wrote:\n\n` +
      `\t${email.body}\n\n\t`;
      
      // Hide error div
      const error = document.querySelector('#error');
      error.innerHTML = '';

      // Load compose view with and set focus on start
      document.querySelector('#compose-view').style.display = 'block';
      form.elements["compose-body"].focus();
      form.elements["compose-body"].setSelectionRange(0, 0);
      document.querySelector('#email-content').style.display = 'none';
    })
}



