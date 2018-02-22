(function($) {

    var netIds = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: "/dartdm/lookup/?term=%QUERY"
    });
    netIds.initialize();

    $(".dartdmLookup").typeahead(null, {
        name: 'net-id',
        displayKey: 'name',
        source: netIds.ttAdapter()
    });

    $( ".dartdmLookup" ).on("typeahead:selected", function(event, object, name) {
        // autofill hidden netid and name fields
        var parent = $(this).parent(".twitter-typeahead");
        var netIdField = $(parent).next(".netIdField").val(object.netid);
        $(netIdField).next(".hiddenNameField").val(object.name);
    });

})(jQuery);
