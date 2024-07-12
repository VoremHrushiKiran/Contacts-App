$(document).ready(function () {
  $("#search-form").submit(function (event) {
    event.preventDefault();
    var searchQuery = $("#search-input").val().trim();
    if (searchQuery !== "") {
      $.ajax({
        type: "GET",
        url: "/search/",
        data: {
          q: searchQuery,
        },
        success: function (response) {
          console.log(response.contacts);
          $("#total").text(response.contacts.length);
          $("tbody").empty();
          if (response.contacts.length > 0) {
            for (var i = 0; i < response.contacts.length; i++) {
              var contact = response.contacts[i];
              var row = `
                  <tr style="cursor: pointer;">
                    <td>${contact.first_name} ${contact.last_name}</td>
                    <td>${contact.phone_number}</td>
                    <td>${contact.email}</td>
                    <td>
                      <a href="/contact/${contact.id}/" class="btn btn-primary btn-sm">View</a>
                      <a href="/update/${contact.id}/" class="btn btn-primary btn-sm">Update</a>
                      <a href="/delete/${contact.id}/" class="btn btn-danger btn-sm">Delete</a>
                    </td>
                  </tr>
                `;
              if (
                contact.address ||
                contact.date_of_birth ||
                contact.category ||
                contact.company_name
              ) {
                row += `
                    <tr class="extra-details" style="display: none;">
                      <td colspan="4">
                  `;
                if (contact.address) {
                  row += `<strong>Address:</strong> ${contact.address}<br>`;
                }
                if (contact.date_of_birth) {
                  row += `<strong>Date of Birth:</strong> ${contact.date_of_birth}<br>`;
                }
                if (contact.category) {
                  row += `<strong>Category:</strong> ${contact.category}<br>`;
                }
                if (contact.company_name) {
                  row += `<strong>Company:</strong> ${contact.company_name}<br>`;
                }
                row += ` 
                      </td>
                    </tr>
                  `;
              }
              $("tbody").append(row);
              console.log(contact);
            }
          } else {
            $("tbody").html('<tr><td colspan="4">No results found.</td></tr>');
          }
        },
        error: function (error) {
          console.log("Error occurred during the search:", error);
        },
      });
    }
  });

  // Toggle extra details on row click
  $("tbody").on("click", "tr", function () {
    $(this).next(".extra-details").toggle();
  });
});
