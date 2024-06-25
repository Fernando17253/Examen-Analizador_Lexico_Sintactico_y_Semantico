let contenedor = [];

function analizar() {
  let codigo = document.getElementById("codigo").value;

  let objetoLexico = {
    valor: "",
    tipo: "",
  };
  $.ajax({
    url: "/analizar", // Esta es la ruta de Flask que manejará la solicitud
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ codigo: codigo }),
    success: function (response) {
      // Iterar sobre la lista de objetos
      response.forEach(function (obj) {
        objetoLexico = {
          valor: obj.valor,
          tipo: obj.tipo,
        };
        contenedor.push(objetoLexico);
      });
      imprimir(contenedor);
      contenedor = [];  // Limpiar el contenedor después de imprimir
    },
    // Esta función se ejecutará si hay un error en la solicitud
    error: function (error) {
      console.error("Error en la solicitud:", error);
    },
  });
}

function imprimir(resultado) {
  let div = document.getElementById("resultado");
  let filas = "";
  let contadorID = 0;
  let contadorReservada = 0;
  let contadorParen = 0;
  let contadorSim = 0;
  let contadorNum = 0;
  let contadorError = 0;
  
  resultado.forEach(function (obj) {
    let datostabla = {
      pr: " ",
      id: " ",
      cad: " ",
      num: " ",
      sim: " ",
      tipo: " ",
      error: " ",
    };
    console.log(`${obj.valor}---${obj.tipo}`);
    
    if (obj.tipo === "ID") {
      datostabla.id = "X";
      contadorID++;
      datostabla.cad = contadorID;
    } else if (["IF", "ELSE", "WHILE", "FOR", "INT", "RETURN", "PRINTF", "INCLUDE", "MAIN", "HEADER"].includes(obj.tipo)) {
      datostabla.pr = "X";
      contadorReservada++;
      datostabla.cad = contadorReservada;
    } else if (obj.tipo === "LPAREN" || obj.tipo === "RPAREN") {
      datostabla.tipo = "PAREN";
      contadorParen++;
      datostabla.cad = contadorParen;
    } else if (["PLUS", "MINUS", "TIMES", "DIVIDE", "EQ", "SEMI", "COMMA"].includes(obj.tipo)) {
      datostabla.sim = "X";
      contadorSim++;
      datostabla.cad = contadorSim;
    } else if (obj.tipo === "NUMBER") {
      datostabla.num = "X";
      contadorNum++;
      datostabla.cad = contadorNum;
    } else if (obj.tipo === "LBRACE" || obj.tipo === "RBRACE") {
      datostabla.tipo = "BRACE";
    } else if (obj.tipo === "ERROR") {
      datostabla.error = "X";
      contadorError++;
      datostabla.cad = contadorError;
    }

    filas += `<tr>
      <td>${obj.valor}</td>
      <td>${datostabla.pr}</td>
      <td>${datostabla.id}</td>
      <td>${datostabla.cad}</td>
      <td>${datostabla.num}</td>
      <td>${datostabla.sim}</td>
      <td>${datostabla.tipo}</td>
      <td>${datostabla.error}</td>
    </tr>`;
  });

  div.innerHTML = `<table class="mi-tabla">
    <tr>
      <th>TOKEN</th>
      <th>PR</th>
      <th>ID</th>
      <th>CANTIDAD</th>
      <th>NUM</th>
      <th>SIM</th>
      <th>TIPO</th>
      <th>ERROR</th>
    </tr>
    ${filas}
  </table>`;
}

function borrar() {
  let codigo = document.getElementById("codigo");
  let div = document.getElementById("resultado");
  let resultadoSintactico = document.getElementById("resultadoSintactico");
  let resultadoSemantico = document.getElementById("resultadoSemantico");
  codigo.value = "";
  div.innerHTML = "";
  resultadoSintactico.innerHTML = "";
  resultadoSemantico.innerHTML = "";
}

function analisisSintactico() {
  let codigo = document.getElementById("codigo").value;
  $.ajax({
    url: "/analizarSintactico",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ codigo: codigo }),
    success: function (response) {
      console.log(response);
      imprimirSintactico(response);
    },
    error: function (error) {
      console.error("Error en la solicitud:", error);
    },
  });
}

function imprimirSintactico(resultado) {
  let resultadoSintactico = document.getElementById("resultadoSintactico");
  resultadoSintactico.innerHTML = resultado.resultado;
}

function analisisSemantico() {
  let codigo = document.getElementById("codigo").value;
  $.ajax({
    url: "/analizarSemantico",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ codigo: codigo }),
    success: function (response) {
      console.log(response);
      imprimirSemantico(response);
    },
    error: function (error) {
      console.error("Error en la solicitud:", error);
    },
  });
}

function imprimirSemantico(resultado) {
  let resultadoS = document.getElementById("resultadoSemantico");
  resultadoS.innerHTML = `${resultado.resultado}`;
}
