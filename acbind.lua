--=============================
--      CONFIG GUI
--=============================

local Players = game:GetService("Players")
local UIS = game:GetService("UserInputService")
local player = Players.LocalPlayer
local PlayerGui = player:WaitForChild("PlayerGui")

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "AutoClickerGui"
screenGui.ResetOnSpawn = false
screenGui.Parent = PlayerGui

local mainFrame = Instance.new("Frame")
mainFrame.Size = UDim2.new(0, 250, 0, 100)
mainFrame.Position = UDim2.new(0.05, 0, 0.2, 0)
mainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
mainFrame.BorderSizePixel = 0
mainFrame.Active = true
mainFrame.Draggable = true
mainFrame.Parent = screenGui

Instance.new("UICorner", mainFrame).CornerRadius = UDim.new(0.1, 0)

local uiStroke = Instance.new("UIStroke")
uiStroke.Thickness = 5
uiStroke.Color = Color3.fromRGB(255, 255, 255)
uiStroke.Parent = mainFrame

--=============================
--     BOTÓN PRINCIPAL
--=============================

local toggleButton = Instance.new("TextButton")
toggleButton.Size = UDim2.new(1, -20, 0, 45)
toggleButton.Position = UDim2.new(0, 10, 0, 10)
toggleButton.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
toggleButton.TextColor3 = Color3.fromRGB(255, 255, 255)
toggleButton.Font = Enum.Font.GothamBold
toggleButton.TextSize = 22
toggleButton.Text = "Click to Bind"
toggleButton.Parent = mainFrame
Instance.new("UICorner", toggleButton).CornerRadius = UDim.new(0.1, 0)

--=============================
--       FOOTER
--=============================

local footer = Instance.new("TextLabel")
footer.Size = UDim2.new(1, -10, 0, 15)
footer.Position = UDim2.new(0, 5, 1, -30)
footer.BackgroundTransparency = 1
footer.TextColor3 = Color3.fromRGB(255, 255, 255)
footer.Font = Enum.Font.GothamSemibold
footer.TextScaled = true
footer.Text = ".gg/B9PR2EZHAK"
footer.Parent = mainFrame

--=============================
--     BOTÓN DE CIERRE (X)
--=============================

local closeButton = Instance.new("TextButton")
closeButton.Size = UDim2.new(0, 25, 0, 25)
closeButton.Text = "X"
closeButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
closeButton.Font = Enum.Font.GothamBold
closeButton.TextSize = 18
closeButton.Parent = screenGui
Instance.new("UICorner", closeButton).CornerRadius = UDim.new(0.3, 0)

closeButton.Position = UDim2.new(0, mainFrame.AbsolutePosition.X + mainFrame.AbsoluteSize.X + 8, 0, mainFrame.AbsolutePosition.Y)

mainFrame:GetPropertyChangedSignal("AbsolutePosition"):Connect(function()
    closeButton.Position = UDim2.new(0, mainFrame.AbsolutePosition.X + mainFrame.AbsoluteSize.X + 8, 0, mainFrame.AbsolutePosition.Y)
end)

--=============================
--  BIND + AUTCLICKER SYSTEM
--=============================

local binding = false
local boundKey = nil
local autoOn = false
local autoLoop = nil

local function updateText()
    toggleButton.Text = boundKey and ("Autoclicker (" .. boundKey.Name .. ")") or "Click to Bind"
end

local function setAuto(state)
    autoOn = state
    toggleButton.BackgroundColor3 = state and Color3.fromRGB(150,50,50) or Color3.fromRGB(50,50,50)

    if autoLoop then autoLoop = nil end
    if not state then return end

    task.spawn(function()
        local id = {}
        autoLoop = id
        while autoOn and autoLoop == id do
            mouse1click()
            task.wait(0.05)
        end
    end)
end

-- CLICK NORMAL PARA EMPEZAR EL BIND
toggleButton.MouseButton1Click:Connect(function()
    binding = true
    toggleButton.Text = "Presiona una tecla..."
    toggleButton.BackgroundColor3 = Color3.fromRGB(80,80,80)
end)

-- DETECTAR TECLA
UIS.InputBegan:Connect(function(input, gpe)
    if gpe then return end

    if binding then
        -- PRIMERA PULSACIÓN: ASIGNAR LA TECLA
        if input.KeyCode ~= Enum.KeyCode.Unknown then
            boundKey = input.KeyCode
            binding = false
            toggleButton.BackgroundColor3 = Color3.fromRGB(50,50,50)
            updateText()
        end
        return
    end

    -- SOLO DESPUÉS DE HABER BIND: ACTIVAR/DESACTIVAR AUTCLICKER
    if boundKey and input.KeyCode == boundKey then
        setAuto(not autoOn)
    end
end)

-- CERRAR GUI
closeButton.MouseButton1Click:Connect(function()
    screenGui:Destroy()
    closeButton:Destroy()
end)
