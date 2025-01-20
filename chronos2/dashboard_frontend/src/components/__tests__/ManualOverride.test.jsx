import React from "react";

import { render, screen, fireEvent,act } from "@testing-library/react";
import { Provider } from "react-redux"; 
import configureStore from "redux-mock-store";
 
import { updateDeviceState } from "../../api/updateState";
import ManualOverride from "../ManualOverride/ManualOverride"; 

jest.mock('../ManualOverride/ManualOverride.css', () => {});
jest.mock("../../api/updateState"); 
jest.mock("../../utils/constant", () => ({
  getDeviceId: jest.fn(() => 1), 
}));

const mockStore = configureStore([]);

it("should render and toggle device states", async () => {
  updateDeviceState.mockResolvedValue({ message: "Updated state successfully" });

  const store = mockStore({
    manualOverride: {
      boiler: true,
      chiller1: false,
      chiller2: true,
      chiller3: false,
      chiller4: true,
    },
  });

  render(
    <Provider store={store}>
      <ManualOverride
        data={{
          devices: [
            { id: 1, state: true },  
            { id: 2, state: false }, 
            { id: 3, state: true },  
            { id: 4, state: false }, 
            { id: 5, state: true },
          ],
        }}
        season="Summer"
      />
    </Provider>
  );

  expect(screen.getByText("Manual Override")).toBeInTheDocument();
  expect(screen.getByText("Boiler")).toBeInTheDocument();
  expect(screen.getByText("Chiller1")).toBeInTheDocument();

  const boilerSwitch = screen.getByText("Boiler").closest('div').querySelector('input');
  await act(async () => {
    fireEvent.click(boilerSwitch);
  });

  expect(updateDeviceState).toHaveBeenCalledTimes(1);
  expect(updateDeviceState).toHaveBeenCalledWith({
    id: 1,
    state: false,
  });

});
