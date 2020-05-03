#!/usr/bin/ruby
# -*- coding: UTF-8 -*-

require "spaceship"

class DevelopPortalHandle
	def login(username,password)
		Spaceship::Portal.login(username,password)
	end

    def createCert(file_format_path_name)
        csr, pkey = Spaceship::Portal.certificate.create_certificate_signing_request
        cert=Spaceship::Portal.certificate.production.create!(csr: csr)
        File.write(file_format_path_name+".key",pkey)
        File.write(file_format_path_name+".cer",cert.download_raw)
        File.write(file_format_path_name+".pem",cert.download)
        File.write(file_format_path_name+".info",cert)
    end

	def createApp(appid,appname)
		app = Spaceship::Portal.app.find(appid)
		if !app then
			app = Spaceship::Portal.app.create!(bundle_id: appid, name: appname)
            app.update_service(Spaceship::Portal.app_service.push_notification.on)
            app.update_service(Spaceship::Portal.app_service.vpn_configuration.on)
		end
	end

    def deleteApp(appid)
		app = Spaceship::Portal.app.find(appid)
		if app then
			app.delete!
		end
	end

    #appstore or inHouse
	def createDistributionProvision(provisioningClass,appid,provisionName,certid)
	    cert = Spaceship::Portal.certificate.Production.find(id=certid)
	    if !cert then
		    cert = Spaceship::Portal.certificate.production.all.last
		end
		profile = provisioningClass.create!(bundle_id: appid,certificate:cert,name:provisionName.split("/")[-1])
        return profile
	end

    #appstore or inHouse
    def downloadDistributionProvision(provisioningClass,appid,provisionName,certid)
        #查找有没有provision文件
        filtered_profiles = provisioningClass.find_by_bundle_id(bundle_id: appid)
        profile = nil
        if  0 < filtered_profiles.length then
            profile = filtered_profiles[0]
            all_devices = Spaceship::Portal.device.all
            profile.devices=all_devices
            profile.update!
            profile = provisioningClass.find_by_bundle_id(bundle_id: appid)[0]
        elsif 0 == filtered_profiles.length then
            profile = createDistributionProvision(provisioningClass,appid,provisionName,certid)
        end

        if profile.status == "Invalid" or profile.status == "Expired"  then
          profile.repair! # yes, that's all you need to repair a profile
        end

        File.write(provisionName, profile.download)
        return provisionName
    end

    def delete_profile(provisioningClass,appid)
        filtered_profiles = provisioningClass.find_by_bundle_id(bundle_id: appid)
        profile = nil
        if  0 < filtered_profiles.length then
            profile = filtered_profiles[0]
            profile.delete!
         end
    end
    def addDevice(device_name,device_udid)
        device = Spaceship::Portal.device.find_by_udid(device_udid, include_disabled: false)
        if !device then
            Spaceship::Portal.device.create!(name: device_name, udid: device_udid)
        end
    end

    def enableDevice(device_udid)
        device=Spaceship::Portal.device.find_by_udid(device_udid, include_disabled: true)
        if device then
            device.enable!
        end
    end

    def disableDevice(device_udid)
        device = Spaceship::Portal.device.find_by_udid(device_udid)
        if device then
            device.disable!
        end
    end

end

    handle = DevelopPortalHandle.new()
    handle.login(ARGV[0],ARGV[1])
    function =  ARGV[2]

    case function
    when "device"
        action = ARGV[3]
        device_udid = ARGV[4]
        device_name = ARGV[5]

        case action
        when "add"
            device_name = device_udid+','+device_udid
            handle.addDevice(device_name,device_udid)
        when "enable"
            handle.enableDevice(device_udid)
        when "disable"
            handle.disableDevice(device_udid)
        end

    when "app"
        action = ARGV[3]
        app_id = ARGV[4]
        app_name = ARGV[5]
		appid = app_id+app_name

        case action
        when "add"
            handle.createApp(appid,app_name)
        when "del"
            handle.deleteApp(appid)
            handle.delete_profile(Spaceship::Portal.provisioning_profile.ad_hoc,appid)
        end
    when "profile"
        action = ARGV[3]
        app_id = ARGV[4]
        app_name = ARGV[5]
        appid = app_id+app_name

        case action
        when "add"
            device_udid = ARGV[6]
            device_name = ARGV[7]
            certid = ARGV[8]
            provisionName = ARGV[9]
            handle.createApp(appid,app_name)
            handle.addDevice(device_name,device_udid)
            provisionPath = handle.downloadDistributionProvision(Spaceship::Portal.provisioning_profile.ad_hoc,appid,provisionName,certid)
        when "del"
            handle.delete_profile(Spaceship::Portal.provisioning_profile.ad_hoc,appid)
        end

    when "cert"
        action = ARGV[3]
        file_format_path_name = ARGV[4]
        case action
        when "add"
            handle.createCert(file_format_path_name)
        end

    when "active"
        puts "active"
    else
        puts "error"
    end


