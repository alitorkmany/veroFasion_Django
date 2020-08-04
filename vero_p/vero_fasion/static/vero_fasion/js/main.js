

//local storage saving currency type
function saveTostorage(currency_type){
  if(sessionStorage){
    sessionStorage.setItem('currency', currency_type);
  }
}

//getting session data and adding currency sign to prices
function getFromstorage(){
  if(sessionStorage.getItem('currency') === 'euro'){
    document.getElementById("opt").innerHTML = 'EUR';
    $('.price-pln').hide();
    $('.price-euro').show();
  }
  else if(sessionStorage.getItem('currency') === 'pln'){
    $('.price-euro').hide();
    $('.price-pln').show();
  }
  else{
    $('.price-euro').hide();
  }
}

//calling gerFromstorage function
$(document).ready(function(){
  getFromstorage();
});

//Dropdowns function
$(document).ready(function () {    
  //Currency dropdown
  $('.currencies button').click(function(){
    $('#opt').text($(this).text());
    let currency_code = $(this).attr('id');
    saveTostorage(currency_code);
    getFromstorage();
  });

  //Color dropdown
  $('.colors a').click(function(){
    $('#drop_color').text('');
    $('#drop_color').html('<span class="caret" id="color-span"></span>');
    $('#color-span').html('<i class="fas fa-square"></i>').css('color', $(this).text()).after($(this).text().toUpperCase());
  });


  //Detail page color dropdown list
  //loading the first color in detail page color dropdown list
  $('#sspan').html('<i class="fas fa-square fa-2x"></i>').css('color', $(".dropdown-uli li:first").text()).after($(".dropdown-uli li:first").text().toUpperCase());
  //adding selected color to detail page color dropdown list on click
  $(".d-item").click(function () {
    $('#dropdown-detail').text('')
    $('#dropdown-detail').html("<span id='sspan' class='caret'></span>")
    $('#sspan').html('<i class="fas fa-square fa-2x"></i>').css('color', $(this).text()).after($(this).text().toUpperCase());
  });

  //Price dropdown
  $('.price a').click(function(){
    $('#drop_price').text($(this).text());
  });

});



//Navigation bar select activor function
(function navbar(){
  $(function() {
		$('.navbar-nav li a').each(function() {
		  if(location.pathname.includes(this.pathname)){
        $('.navbar ul li').removeClass('active');
        $(this).parent().toggleClass('active', this.pathname);
      }
		});
	});
})();

//home selected li active function
(function home_navbar(){
  $(function() {
    $('.home_nav li a').each(function() {
      if(location.href.includes(this.href)){
        console.log(this.pathname)
        $('.home_nav li').removeClass('active');
        $(this).parent().toggleClass('active', this.pathname);
      }
    });
  });
})();

//women-page navbar selected li active function
(function women_page_navbar(){
  $(function() {
    $('.woman_nav li a').each(function() {
      if(location.pathname.includes(this.pathname)){
        $('.woman_nav li').removeClass('active');
        $(this).parent().toggleClass('active', this.pathname);
      }
    });
  });
})();

//women-page selected li active color dropdown function
(function women_page_colorbar(){
  $(function() {
    $('.colors li a').each(function() {
      if(location.href.includes(this.href)){
        $('.colors li').removeClass('selected');
        $(this).parent().toggleClass('selected', this.pathname);
      }
    });
  });
})();

//set color dropdown to selected color
$(document).ready(function(){
  if($('.colors li').hasClass('selected')){
    $('#drop_color').text('');
    $('#drop_color').html('<span class="caret" id="color-span"></span>');
    $('#color-span').html('<i class="fas fa-square"></i>').css('color',  $('.selected a').attr('id')).after($('.selected a').text().toUpperCase());
  }
});

//women-page selected li active price dropdown function
(function women_page_pricebar(){
  $(function() {
    $('.price li a').each(function() {
      if(this.pathname+this.search === location.pathname+location.search){
        $('.price li').removeClass('choosen');
        $(this).parent().toggleClass('choosen', this.pathname);
      }
    });
  });
})();

//set price dropdown to selected price range
$(document).ready(function(){
  if($('.price li').hasClass('choosen')){
    $('#drop_price').text($('.choosen a').text());
  }
});

//retreiving item count for basket
$(document).ready(function(){
  $.ajax({
    url: '/cart/cart-item-count/',
    dataType: 'json',
    success: function(data){
      if(data){
        $('#basket').text(data.count);
      }
    }
  });
});
//Sending data to popup modal and calling add_to_cart view function
function popup(param){

  $(param).click(function(){
    //calling ad to cart view
    if(param === '.btn-detail' || param === '.a-btn'){

      $.ajax({
        url: '/cart/add-to-cart/',
        data: {
          'id': $(this).attr('id'),
          'color': $(this).attr('colour'),
          'count': $("#q-counter").text()
        },
        dataType: 'json',
        success: function(data){
            if(data){
            $('#basket').text(data.count);
          }
        }
      });
    } 

    //query for popup
    $.ajax({
      //type: 'POST',
      url: '/product-detail/',
      data: {'id': $(this).attr('id')},
      dataType: 'json',
      success: function(data){
        
        if(data){
          $('#modal-ptitle').text(data.title);
          $("#modal-image").attr("src",data.image_url);
          $("#modal-color").text('KOLOR:  ' + data.color.toUpperCase());
          if($("#q-counter").text() != ""){
            $("#modal-quantity").text('Ilość:  ' + $("#q-counter").text());
          }

          if(sessionStorage.getItem('currency') === 'euro')
          {
            if(data.sale_euro){
              $('#modal-p_price').text(data.sale_euro);
            }
            else{
              $('#modal-p_price').text(data.price_euro);
            }
          }
          else
          {
            if(data.sale_price){
              $('#modal-p_price').text(data.sale_price);
            }
            else{
              $('#modal-p_price').text(data.price);
            }
          }

        }
      }
    });
  });
}



//Supscription
 $(document).ready(function(){
  let form = $('#subs-form');
  form.submit(function(e){
    e.preventDefault();

    $("#load").html('<i class="fa fa-circle-o-notch fa-spin"></i> Subscribe')

    $.ajax({
      type: 'POST',
      url: '/subscription/',
      data: {
        email: $('#subs-mail').val(),
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
      },
      success: function(data){
        $("#load").html('Subscribe')
        $('#subs-mail').val("");
        $("#sub-message").text(data.message);
        $(".sub-alert").show();

        setTimeout(function(){
          $(".sub-alert").hide(); 
       }, 4000);
      }
    });
  });
 });


 