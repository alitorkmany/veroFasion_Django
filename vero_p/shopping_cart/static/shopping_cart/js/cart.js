//Checkout billing form submistion
 $(document).ready(function(){
  let form = $('#bill-form');
  form.submit(function(e){
    e.preventDefault();

    $.ajax({
      type: 'POST',
      url: '/cart/check-out/',
      data: {
        firstname: $('#inputNameF').val(),
        lastname: $('#inputLastF').val(),
        address: $('#inputAddressF').val(),
        email: $('#inputEmail4F').val(),
        phone: $('#phoneF').val(),
        country: $('#inputCountryF').val(),
        postalcode: $('#inputZipF').val(),
        city: $('#inputCityF').val(),
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
      },
      success: function(data){
        if(data){
          $.ajax({
            type: 'GET',
            url: '/cart/shipping-address/',
            success: function(is_true){
              if(is_true.shipping_address === false){
                $('#delivery-fullname').text(data.fullname);
                $('#delivery-address').text(data.fulladdress);
              }
            }
          });

          $('#bill-fullname').text(data.fullname);
          $('#bill-address').text(data.fulladdress);
          $('#bill-form').hide();
          $('#billing-div').show();
          $('#delivery-div').show();
          $('#card-div').show();
        }
      }
    });
  });
 });

  //Checkout shipping address form submistion
 $(document).ready(function(){
  let form = $('#shipping-form');
  form.submit(function(e){
    e.preventDefault();

    $.ajax({
      type: 'POST',
      url: '/cart/shipping-address/',
      data: {
        firstname: $('#inputName').val(),
        lastname: $('#inputLast').val(),
        address: $('#inputAddress').val(),
        email: $('#inputEmail4').val(),
        phone: $('#phone').val(),
        country: $('#inputCountry').val(),
        postalcode: $('#inputZip').val(),
        city: $('#inputCity').val(),
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
      },
      success: function(data){
        if(data){
          $('#delivery-fullname').text(data.fullname);
          $('#delivery-address').text(data.fulladdress);
          $('#delivery-modal').modal('toggle');
        }
      }
    });
  });
 });

//****************************** STRIPE FUNCTIONS ************************************************
function stripefy(pub_key, client_secret){
  return function(){
    var stripe = Stripe(pub_key);
    var elements = stripe.elements();

    // Set up Stripe.js and Elements to use in checkout form
    var style = {
      base: {
        color: "#32325d",
      }
    };

    var card = elements.create("card", { style: style });
    card.mount("#card-element");

    card.addEventListener('change', function(event) {
      var displayError = document.getElementById('card-errors');
      if (event.error) {
        displayError.textContent = event.error.message;
      } else {
        displayError.textContent = '';
      }
    });

    var clientSecret = client_secret;

    var form = document.getElementById("card-form");
    var submitBtn = document.getElementById("submit");
    submitBtn.addEventListener('click', function(){
      $('#pleaseWaitDialog').modal();
        stripe.confirmCardPayment(clientSecret, {
    payment_method: {card: card}
      }).then(function(result) {
        if (result.error) {
          // Show error to your customer (e.g., insufficient funds)
          $('#pleaseWaitDialog').modal('hide');
          alert(result.error.message);
        } else {
          // The payment has been processed!
          if (result.paymentIntent.status === 'succeeded') {
            $('#pleaseWaitDialog').modal('hide');
            // Show a success message to your customer
            // There's a risk of the customer closing the window before callback execution
            // Set up a webhook or plugin to listen for the payment_intent.succeeded event
            // that handles any business critical post-payment actions
            
            form.submit();
            
          }
        }
      });
    });
  }
}