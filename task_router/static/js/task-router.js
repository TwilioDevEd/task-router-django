$(function() {
  var currentAgentId;
  var currentConnection;
  var $callStatus = $('#call-status');
  var $connectAgent1Button = $("#connect-agent1-button");
  var $connectAgent2Button = $("#connect-agent2-button");

  var $answerCallButton = $("#answer-call-button");
  var $hangupCallButton = $("#hangup-call-button");
  var $dialAgent2Button = $("#dial-agent2-button");

  $connectAgent1Button.on('click', { agentId: 'agent1' }, agentClickHandler);
  $connectAgent2Button.on('click', { agentId: 'agent2' }, agentClickHandler);
  $hangupCallButton.on('click', hangUp);
  $dialAgent2Button.on('click', dialAgent2);

  function fetchToken(agentId) {
    $.post('/' + agentId + '/token', {}, function(data) {
      currentAgentId = data.agentId;
      connectClient(data.token)
    }, 'json');
  }

  function connectClient(token) {
    Twilio.Device.setup(token);
  }

  Twilio.Device.ready(function (device) {
    updateCallStatus("Ready");
    agentConnectedHandler(device._clientName);
  });

  // Callback for when Twilio Client receives a new incoming call
  Twilio.Device.incoming(function(connection) {
    currentConnection = connection;
    updateCallStatus("Incoming support call");

    // Set a callback to be executed when the connection is accepted
    connection.accept(function() {
      updateCallStatus("In call with customer");
      $answerCallButton.prop('disabled', true);
      $hangupCallButton.prop('disabled', false);
      $dialAgent2Button.prop('disabled', false);
    });

    // Set a callback on the answer button and enable it
    $answerCallButton.click(function() {
      connection.accept();
    });
    $answerCallButton.prop('disabled', false);
  });

  /* Report any errors to the call status display */
  Twilio.Device.error(function (error) {
    updateCallStatus("ERROR: " + error.message);
    disableConnectButtons(false);
  });

  // Callback for when the call finalizes
  Twilio.Device.disconnect(function(connection) {
    callEndedHandler(connection.device._clientName);
  });

  function dialAgent2() {
    $.post('/conference/' + currentAgentId + '/call')
  }

  /* End a call */
  function hangUp() {
    Twilio.Device.disconnectAll();
  }

  function agentClickHandler(e) {
    var agentId = e.data.agentId;
    disableConnectButtons(true);
    fetchToken(agentId);
  }

  function agentConnectedHandler(agentId) {
    $('#connect-agent-row').addClass('hidden');
    $('#connected-agent-row').removeClass('hidden');
    updateCallStatus("Connected as: " + agentId);

    if (agentId === 'agent1') {
      $dialAgent2Button.removeClass('hidden').prop('disabled', true);
    }
    else {
      $dialAgent2Button.addClass('hidden')
    }
  }

  function callEndedHandler(agentId) {
    $dialAgent2Button.prop('disabled', true);
    $hangupCallButton.prop('disabled', true);
    $answerCallButton.prop('disabled', true)
    updateCallStatus("Connected as: " + agentId);
  }

  function disableConnectButtons(disable) {
    $connectAgent1Button.prop('disabled', disable);
    $connectAgent2Button.prop('disabled', disable);
  }

  function updateCallStatus(status) {
    $callStatus.text(status);
  }
});
